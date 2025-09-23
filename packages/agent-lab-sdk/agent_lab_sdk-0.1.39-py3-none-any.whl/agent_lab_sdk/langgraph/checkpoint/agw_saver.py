from __future__ import annotations

import asyncio
import base64
import logging
import os
from contextlib import asynccontextmanager
from random import random
from typing import Any, AsyncIterator, Dict, Iterable, Iterator, Optional, Sequence, Tuple

import orjson
from langgraph.checkpoint.serde.types import ChannelProtocol

import httpx
from langchain_core.runnables import RunnableConfig

from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    get_checkpoint_id,
    get_checkpoint_metadata,
)
from langgraph.checkpoint.serde.base import SerializerProtocol
from langgraph.checkpoint.serde.encrypted import EncryptedSerializer

from .serde import Serializer
from agent_lab_sdk.metrics import get_metric

__all__ = ["AsyncAGWCheckpointSaver"]

logger = logging.getLogger(__name__)

AGW_METRIC_LABELS = ["method", "endpoint"]
AGW_HTTP_SUCCESS = get_metric(
    "counter",
    "agw_http_success_total",
    "Number of successful AGW HTTP requests",
    labelnames=AGW_METRIC_LABELS,
)
AGW_HTTP_ERROR = get_metric(
    "counter",
    "agw_http_error_total",
    "Number of failed AGW HTTP request attempts",
    labelnames=AGW_METRIC_LABELS,
)
AGW_HTTP_FINAL_ERROR = get_metric(
    "counter",
    "agw_http_final_error_total",
    "Number of AGW HTTP requests that failed after retries",
    labelnames=AGW_METRIC_LABELS,
)

TYPED_KEYS = ("type", "blob")


def _b64decode_strict(value: str) -> bytes | None:
    try:
        return base64.b64decode(value, validate=True)
    except Exception:
        return None

# ------------------------------------------------------------------ #
# helpers for Py < 3.10
# ------------------------------------------------------------------ #
try:
    anext  # type: ignore[name-defined]
except NameError:  # pragma: no cover

    async def anext(it):
        return await it.__anext__()


class AsyncAGWCheckpointSaver(BaseCheckpointSaver):
    """Persist checkpoints in Agent-Gateway с помощью `httpx` async client."""

    # ---------------------------- init / ctx -------------------------
    def __init__(
        self,
        base_url: str = "http://localhost",
        *,
        serde: SerializerProtocol | None = None,
        timeout: int | float = 10,
        api_key: str | None = None,
        extra_headers: Dict[str, str] | None = None,
        verify: bool = True,
    ):
        if not serde:
            base_serde: SerializerProtocol = Serializer()
            aes_key = (
                os.getenv("LANGGRAPH_AES_KEY")
                or os.getenv("AGW_AES_KEY")
                or os.getenv("AES_KEY")
            )
            if aes_key:
                base_serde = EncryptedSerializer.from_pycryptodome_aes(
                    base_serde, key=aes_key
                )
            serde = base_serde
        super().__init__(serde=serde)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.loop = asyncio.get_running_loop()

        raw_attempts = os.getenv("AGW_HTTP_MAX_RETRIES")
        if raw_attempts is None:
            self.retry_max_attempts = 3
        else:
            try:
                self.retry_max_attempts = max(int(raw_attempts), 1)
            except ValueError:
                logger.warning(
                    "Env %s expected int, got %r; using default %s",
                    "AGW_HTTP_MAX_RETRIES",
                    raw_attempts,
                    3,
                )
                self.retry_max_attempts = 3

        raw_backoff_base = os.getenv("AGW_HTTP_RETRY_BACKOFF_BASE")
        if raw_backoff_base is None:
            self.retry_backoff_base = 0.5
        else:
            try:
                self.retry_backoff_base = max(float(raw_backoff_base), 0.0)
            except ValueError:
                logger.warning(
                    "Env %s expected float, got %r; using default %.3f",
                    "AGW_HTTP_RETRY_BACKOFF_BASE",
                    raw_backoff_base,
                    0.5,
                )
                self.retry_backoff_base = 0.5

        raw_backoff_max = os.getenv("AGW_HTTP_RETRY_BACKOFF_MAX")
        if raw_backoff_max is None:
            self.retry_backoff_max = 5.0
        else:
            try:
                self.retry_backoff_max = max(float(raw_backoff_max), 0.0)
            except ValueError:
                logger.warning(
                    "Env %s expected float, got %r; using default %.3f",
                    "AGW_HTTP_RETRY_BACKOFF_MAX",
                    raw_backoff_max,
                    5.0,
                )
                self.retry_backoff_max = 5.0

        raw_jitter = os.getenv("AGW_HTTP_RETRY_JITTER")
        if raw_jitter is None:
            self.retry_jitter = 0.25
        else:
            try:
                self.retry_jitter = max(float(raw_jitter), 0.0)
            except ValueError:
                logger.warning(
                    "Env %s expected float, got %r; using default %.3f",
                    "AGW_HTTP_RETRY_JITTER",
                    raw_jitter,
                    0.25,
                )
                self.retry_jitter = 0.25

        self.headers: Dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if extra_headers:
            self.headers.update(extra_headers)
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

        self._verify = verify
        self._client: httpx.AsyncClient | None = None

    def _create_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
            verify=self._verify,
            trust_env=True,
        )

    def _ensure_client(self) -> httpx.AsyncClient:
        client = self._client
        if client is None or client.is_closed:
            if client is not None and client.is_closed:
                logger.debug("Recreating closed httpx.AsyncClient for AGW")
            client = self._create_client()
            self._client = client
        return client

    def _compute_retry_delay(self, attempt: int) -> float:
        if attempt <= 0:
            attempt = 1
        if self.retry_backoff_base <= 0:
            delay = 0.0
        else:
            delay = self.retry_backoff_base * (2 ** (attempt - 1))
            if self.retry_backoff_max > 0:
                delay = min(delay, self.retry_backoff_max)
        if self.retry_jitter > 0:
            delay += self.retry_jitter * random()
        return delay

    async def __aenter__(self):  # noqa: D401
        return self

    async def __aexit__(self, exc_type, exc, tb):  # noqa: D401
        if self._client is not None:
            try:
                await self._client.aclose()
            except Exception as close_exc:  # pragma: no cover - best effort
                logger.debug("Failed to close AGW httpx.AsyncClient: %s", close_exc)
            finally:
                self._client = None

    # ----------------------- universal dump/load ---------------------
    # def _safe_dump(self, obj: Any) -> Any:
    #     """self.serde.dump → гарантированная JSON-строка."""
    #     dumped = self.serde.dumps(obj)
    #     if isinstance(dumped, (bytes, bytearray)):
    #         return base64.b64encode(dumped).decode()  # str
    #     return dumped  # уже json-совместимо

    def _safe_dump(self, obj: Any) -> Any:
        """bytes → python-object; fallback base64 для реально бинарных данных."""
        dumped = self.serde.dumps(obj)
        if isinstance(dumped, (bytes, bytearray)):
            try:
                # 1) bytes → str
                s = dumped.decode()
                # 2) str JSON → python (list/dict/scalar)
                return orjson.loads(s)
            except (UnicodeDecodeError, orjson.JSONDecodeError):
                # не UTF-8 или не JSON → base64
                return base64.b64encode(dumped).decode()
        return dumped

    def _safe_load(self, obj: Any) -> Any:
        if obj is None:
            return None

        if isinstance(obj, dict):
            if all(k in obj for k in TYPED_KEYS):
                t = obj.get("type")
                blob = obj.get("blob")
                if blob is None:
                    try:
                        return self.serde.loads_typed((t, None))
                    except Exception:
                        return obj
                if isinstance(blob, str):
                    payload = _b64decode_strict(blob)
                    if payload is not None:
                        try:
                            return self.serde.loads_typed((t, payload))
                        except Exception:
                            # fall back to generic handling below
                            pass
            try:
                return self.serde.loads(orjson.dumps(obj))
            except Exception:
                return obj

        if isinstance(obj, (list, tuple)):
            if (
                len(obj) == 2
                and isinstance(obj[0], str)
                and (obj[1] is None or isinstance(obj[1], str))
            ):
                blob = obj[1]
                if blob is None:
                    try:
                        return self.serde.loads_typed((obj[0], None))
                    except Exception:
                        pass
                elif isinstance(blob, str):
                    payload = _b64decode_strict(blob)
                    if payload is not None:
                        try:
                            return self.serde.loads_typed((obj[0], payload))
                        except Exception:
                            pass
            try:
                return self.serde.loads(orjson.dumps(list(obj)))
            except Exception:
                return obj

        if isinstance(obj, str):
            try:
                return self.serde.loads(obj.encode())
            except Exception:
                payload = _b64decode_strict(obj)
                if payload is not None:
                    try:
                        return self.serde.loads(payload)
                    except Exception:
                        pass
                return obj

        try:
            return self.serde.loads(obj)
        except Exception:
            return obj

    # def _safe_load(self, obj: Any) -> Any:
    #     """Обратная операция к _safe_dump."""
    #     if isinstance(obj, str):
    #         try:
    #             return self.serde.load(base64.b64decode(obj))
    #         except Exception:
    #             # не base64 — обычная строка
    #             return self.serde.load(obj)
    #     return self.serde.load(obj)

    # ----------------------- config <-> api --------------------------
    def _to_api_config(self, cfg: RunnableConfig | None) -> Dict[str, Any]:
        if not cfg:
            return {}
        c = cfg.get("configurable", {})
        res: Dict[str, Any] = {
            "threadId": c.get("thread_id", ""),
            "checkpointNs": c.get("checkpoint_ns", ""),
        }
        if cid := c.get("checkpoint_id"):
            res["checkpointId"] = cid
        if ts := c.get("thread_ts"):
            res["threadTs"] = ts
        return res

    # --------------------- checkpoint (de)ser ------------------------
    def _encode_cp(self, cp: Checkpoint) -> Dict[str, Any]:
        pending: list[Any] = []
        for item in cp.get("pending_sends", []) or []:
            try:
                channel, value = item
            except Exception:
                pending.append(item)
                continue
            pending.append([channel, self._safe_dump(value)])
        return {
            "v": cp["v"],
            "id": cp["id"],
            "ts": cp["ts"],
            "channelValues": {k: self._safe_dump(v) for k, v in cp["channel_values"].items()},
            "channelVersions": cp["channel_versions"],
            "versionsSeen": cp["versions_seen"],
            "pendingSends": pending,
        }

    def _decode_cp(self, raw: Dict[str, Any]) -> Checkpoint:
        pending_sends: list[Tuple[str, Any]] = []
        for obj in raw.get("pendingSends", []) or []:
            if isinstance(obj, dict) and "channel" in obj:
                channel = obj["channel"]
                value_payload: Any = obj.get("value")
                if value_payload is None and all(k in obj for k in TYPED_KEYS):
                    value_payload = {k: obj[k] for k in TYPED_KEYS}
                pending_sends.append((channel, self._safe_load(value_payload)))
            elif isinstance(obj, (list, tuple)) and len(obj) >= 2:
                channel = obj[0]
                value_payload = obj[1]
                pending_sends.append((channel, self._safe_load(value_payload)))
            else:
                pending_sends.append(obj)  # сохраняем как есть, если формат неизвестен
        return Checkpoint(
            v=raw["v"],
            id=raw["id"],
            ts=raw["ts"],
            channel_values={k: self._safe_load(v) for k, v in raw["channelValues"].items()},
            channel_versions=raw["channelVersions"],
            versions_seen=raw["versionsSeen"],
            pending_sends=pending_sends,
        )

    def _decode_config(self, raw: Dict[str, Any] | None) -> Optional[RunnableConfig]:
        if not raw:
            return None
        return RunnableConfig(
            tags=raw.get("tags"),
            metadata=raw.get("metadata"),
            callbacks=raw.get("callbacks"),
            run_name=raw.get("run_name"),
            max_concurrency=raw.get("max_concurrency"),
            recursion_limit=raw.get("recursion_limit"),
            configurable=self._decode_configurable(raw.get("configurable") or {}),
        )

    def _decode_configurable(self, raw: Dict[str, Any]) -> dict[str, Any]:
        return {
            "thread_id": raw.get("threadId"),
            "thread_ts": raw.get("threadTs"),
            "checkpoint_ns": raw.get("checkpointNs"),
            "checkpoint_id": raw.get("checkpointId")
        }

    # metadata (de)ser
    def _enc_meta(self, md: CheckpointMetadata) -> CheckpointMetadata:
        if not md:
            return {}
        out: CheckpointMetadata = {}
        for k, v in md.items():
            out[k] = self._enc_meta(v) if isinstance(v, dict) else self._safe_dump(v)  # type: ignore[assignment]
        return out

    def _dec_meta(self, md: Any) -> Any:
        if isinstance(md, dict):
            return {k: self._dec_meta(v) for k, v in md.items()}
        return self._safe_load(md)

    # ------------------------ HTTP wrapper ---------------------------
    async def _http(
        self,
        method: str,
        path: str,
        *,
        ok_statuses: Iterable[int] | None = None,
        **kw,
    ) -> httpx.Response:
        if "json" in kw:
            payload = kw.pop("json")
            kw["data"] = orjson.dumps(payload)
            logger.debug("AGW HTTP payload: %s", kw["data"].decode())

        ok_set = set(ok_statuses) if ok_statuses is not None else set()

        attempt = 1
        while True:
            client = self._ensure_client()
            try:
                resp = await client.request(method, path, **kw)
            except httpx.RequestError as exc:
                AGW_HTTP_ERROR.labels(method, path).inc()
                logger.warning(
                    "AGW request %s %s failed on attempt %d/%d: %s",
                    method,
                    path,
                    attempt,
                    self.retry_max_attempts,
                    exc,
                )
                if attempt >= self.retry_max_attempts:
                    AGW_HTTP_FINAL_ERROR.labels(method, path).inc()
                    if self._client is not None:
                        try:
                            await self._client.aclose()
                        except Exception as close_exc:  # pragma: no cover
                            logger.debug(
                                "Failed to close AGW httpx.AsyncClient: %s",
                                close_exc,
                            )
                        finally:
                            self._client = None
                    raise

                if self._client is not None:
                    try:
                        await self._client.aclose()
                    except Exception as close_exc:  # pragma: no cover
                        logger.debug(
                            "Failed to close AGW httpx.AsyncClient: %s",
                            close_exc,
                        )
                    finally:
                        self._client = None
                delay = self._compute_retry_delay(attempt)
                if delay > 0:
                    await asyncio.sleep(delay)
                attempt += 1
                continue

            status = resp.status_code
            if status < 400 or status in ok_set:
                AGW_HTTP_SUCCESS.labels(method, path).inc()
                return resp

            AGW_HTTP_ERROR.labels(method, path).inc()
            if status in (404, 406):
                AGW_HTTP_FINAL_ERROR.labels(method, path).inc()
                return resp

            if attempt >= self.retry_max_attempts:
                AGW_HTTP_FINAL_ERROR.labels(method, path).inc()
                return resp

            try:
                await resp.aclose()
            except Exception as exc:  # pragma: no cover - best effort
                logger.debug("Failed to close AGW httpx.Response before retry: %s", exc)

            if self._client is not None:
                try:
                    await self._client.aclose()
                except Exception as close_exc:  # pragma: no cover
                    logger.debug(
                        "Failed to close AGW httpx.AsyncClient: %s",
                        close_exc,
                    )
                finally:
                    self._client = None
            delay = self._compute_retry_delay(attempt)
            if delay > 0:
                await asyncio.sleep(delay)
            attempt += 1

    # -------------------- api -> CheckpointTuple ----------------------
    def _to_tuple(self, node: Dict[str, Any]) -> CheckpointTuple:
        pending = None
        if node.get("pendingWrites"):
            pending = []
            for w in node["pendingWrites"]:
                if isinstance(w, dict):
                    first = w.get("first")
                    second = w.get("second")
                    third = w.get("third")
                    if third is None and isinstance(second, dict) and all(
                        k in second for k in TYPED_KEYS
                    ):
                        third = second
                    pending.append((first, second, self._safe_load(third)))
                elif isinstance(w, (list, tuple)):
                    if len(w) == 3:
                        first, second, third = w
                    elif len(w) == 2:
                        first, second = w
                        third = None
                    else:
                        continue
                    pending.append((first, second, self._safe_load(third)))
        return CheckpointTuple(
            config=self._decode_config(node.get("config")),
            checkpoint=self._decode_cp(node["checkpoint"]),
            metadata=self._dec_meta(node.get("metadata")),
            parent_config=self._decode_config(node.get("parentConfig")),
            pending_writes=pending,
        )

    # =================================================================
    # async-методы BaseCheckpointSaver
    # =================================================================
    async def aget_tuple(self, cfg: RunnableConfig) -> CheckpointTuple | None:
        cid = get_checkpoint_id(cfg)
        api_cfg = self._to_api_config(cfg)
        tid = api_cfg["threadId"]

        if cid:
            path = f"/checkpoint/{tid}/{cid}"
            params = {"checkpointNs": api_cfg.get("checkpointNs", "")}
        else:
            path = f"/checkpoint/{tid}"
            params = None

        resp = await self._http("GET", path, params=params)
        logger.debug("AGW aget_tuple response: %s", resp.text)

        if not resp.text:
            return None
        if resp.status_code in (404, 406):
            return None
        resp.raise_for_status()
        return self._to_tuple(resp.json())

    async def alist(
        self,
        cfg: RunnableConfig | None,
        *,
        filter: Dict[str, Any] | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[CheckpointTuple]:
        payload = {
            "config": self._to_api_config(cfg) if cfg else None,
            "filter": filter,
            "before": self._to_api_config(before) if before else None,
            "limit": limit,
        }
        resp = await self._http("POST", "/checkpoint/list", json=payload)
        logger.debug("AGW alist response: %s", resp.text)
        resp.raise_for_status()
        for item in resp.json():
            yield self._to_tuple(item)

    async def aput(
        self,
        cfg: RunnableConfig,
        cp: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        payload = {
            "config": self._to_api_config(cfg),
            "checkpoint": self._encode_cp(cp),
            "metadata": self._enc_meta(get_checkpoint_metadata(cfg, metadata)),
            "newVersions": new_versions,
        }
        resp = await self._http("POST", "/checkpoint", json=payload)
        logger.debug("AGW aput response: %s", resp.text)
        resp.raise_for_status()
        return resp.json()["config"]

    async def aput_writes(
        self,
        cfg: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        enc = [{"first": ch, "second": self._safe_dump(v)} for ch, v in writes]
        payload = {
            "config": self._to_api_config(cfg),
            "writes": enc,
            "taskId": task_id,
            "taskPath": task_path,
        }
        resp = await self._http("POST", "/checkpoint/writes", json=payload)
        logger.debug("AGW aput_writes response: %s", resp.text)
        resp.raise_for_status()

    async def adelete_thread(self, thread_id: str) -> None:
        resp = await self._http("DELETE", f"/checkpoint/{thread_id}")
        resp.raise_for_status()

    # =================================================================
    # sync-обёртки
    # =================================================================
    def _run(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result()

    def list(
        self,
        cfg: RunnableConfig | None,
        *,
        filter: Dict[str, Any] | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> Iterator[CheckpointTuple]:
        aiter_ = self.alist(cfg, filter=filter, before=before, limit=limit)
        while True:
            try:
                yield self._run(anext(aiter_))
            except StopAsyncIteration:
                break

    def get_tuple(self, cfg: RunnableConfig) -> CheckpointTuple | None:
        return self._run(self.aget_tuple(cfg))

    def put(
        self,
        cfg: RunnableConfig,
        cp: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        return self._run(self.aput(cfg, cp, metadata, new_versions))

    def put_writes(
        self,
        cfg: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        self._run(self.aput_writes(cfg, writes, task_id, task_path))

    def delete_thread(self, thread_id: str) -> None:
        self._run(self.adelete_thread(thread_id))

    def get_next_version(self, current: Optional[str], channel: ChannelProtocol) -> str:
        if current is None:
            current_v = 0
        elif isinstance(current, int):
            current_v = current
        else:
            current_v = int(current.split(".")[0])
        next_v = current_v + 1
        next_h = random()
        return f"{next_v:032}.{next_h:016}"

    # ------------------------------------------------------------------ #
    # Convenience factory                                                #
    # ------------------------------------------------------------------ #
    @classmethod
    @asynccontextmanager
    async def from_base_url(
        cls,
        base_url: str,
        *,
        api_key: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator["AsyncAGWCheckpointSaver"]:
        saver = cls(base_url, api_key=api_key, **kwargs)
        try:
            yield saver
        finally:
            if saver._client is not None:
                try:
                    await saver._client.aclose()
                except Exception as close_exc:  # pragma: no cover - best effort
                    logger.debug("Failed to close AGW httpx.AsyncClient: %s", close_exc)
                finally:
                    saver._client = None
