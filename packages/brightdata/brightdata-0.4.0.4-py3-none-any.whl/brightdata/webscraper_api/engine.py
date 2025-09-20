# brightdata/engine.py

from __future__ import annotations
"""
brightdata.engine
=================
One central, async-only helper that owns every low-level detail of talking to
Bright Data’s *dataset* API—**without** a long-lived session.

► Creates a fresh `aiohttp.ClientSession` per call  
► Generates monotonically-increasing trace-IDs  
► Triggers jobs (`sync_mode=async` by default)  
► Polls `/progress/{snapshot_id}`  
► Downloads `/snapshot/{snapshot_id}`  
► Records rich timing metadata for every snapshot  
► Tiny public surface for all specialized scrapers  
"""

import asyncio
import logging
import os
import ssl
import time
import urllib.parse
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp
import tldextract

from brightdata.models import ScrapeResult
from brightdata.utils import _BD_URL_RE

log = logging.getLogger(__name__)


class BrightdataEngine:
    """Process-wide engine—**no** shared session, all sessions are per-call."""
    
    # timing & trace metadata (still shared for introspection)
    _snap_meta: Dict[str, Dict[str, Any]] = {}
    _trace_lock = asyncio.Lock()
    _ctr: int = 0
    
    COST_PER_RECORD = 0.001 

    def __init__(self, bearer_token: Optional[str] = None, *, timeout: int = 40):
        self._token = bearer_token or os.getenv("BRIGHTDATA_TOKEN")
        if not self._token:
            raise RuntimeError("Provide BRIGHTDATA_TOKEN env var or pass bearer_token")
        # client timeout for every new session
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    async def _next_trace_id(self) -> str:
        async with BrightdataEngine._trace_lock:
            BrightdataEngine._ctr += 1
            return f"bd-{int(time.time()*1e6):x}-{BrightdataEngine._ctr}"
        


    async def trigger(
        self,
        payload: List[dict[str, Any]],
        *,
        dataset_id: str,
        include_errors: bool = True,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        POST to /trigger (always async mode) → returns snapshot_id or None.

        If the HTTPS handshake fails because the local machine cannot verify
        Bright Data’s certificate, raise RuntimeError with a helpful hint.
        All other network/HTTP problems still return None (legacy behaviour).
        """
        params = {
            "dataset_id":     dataset_id,
            "include_errors": str(include_errors).lower(),
            "format":         "json",
            "sync_mode":      "async",
            **(extra_params or {}),
        }

        sent_at  = datetime.utcnow()
        trace_id = await self._next_trace_id()

        url = "https://api.brightdata.com/datasets/v3/trigger"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type":  "application/json",
        }

        # ─────────────── one brand-new session per call ────────────────
        async with aiohttp.ClientSession(
            timeout=self._timeout,
            headers=headers,
            trust_env=True,
        ) as sess:
            try:
                async with sess.post(url, params=params, json=payload) as resp:
                    resp.raise_for_status()
                    data = await resp.json()

            # ── special case: SSL root CA missing on the host machine ──
            except aiohttp.ClientConnectorCertificateError as e:
                raise RuntimeError(
                    "SSL certificate verification failed while contacting "
                    "api.brightdata.com.  On macOS this usually means the Python "
                    "installation is missing the system root certificates.  "
                    "Run the ‘Install Certificates.command’ that ships with "
                    "the official python.org installer, or try:\n"
                    "    python -m pip install --upgrade certifi"
                ) from e
            except ssl.SSLCertVerificationError as e:        # defence-in-depth
                raise RuntimeError(
                    f"SSL certificate verification failed: {e}"
                ) from e

            # ── any other network / HTTP error: legacy behaviour ─────────
            except Exception as e:
                log.debug("trigger %s failed: %s", dataset_id, e)
                return None

        # ------------------- happy path: got a snapshot_id ---------------
        sid = data.get("snapshot_id")
        if not sid:
            log.debug("trigger response w/o snapshot_id: %s", data)
            return None

        # record timing / trace metadata
        first_url     = payload[0].get("url", "") if payload else ""
        root_override = tldextract.extract(first_url).domain or None
        BrightdataEngine._snap_meta[sid] = {
            "trace_id":                trace_id,
            "request_sent_at":         sent_at,
            "snapshot_id_received_at": datetime.utcnow(),
            "snapshot_polled_at":      [],
            "data_received_at":        None,
            "root_override":           root_override,
        }
        return sid

    # async def trigger(
    #     self,
    #     payload: List[dict[str, Any]],
    #     *,
    #     dataset_id: str,
    #     include_errors: bool = True,
    #     extra_params: Optional[Dict[str, Any]] = None,
    # ) -> Optional[str]:
    #     """
    #     POST to /trigger (always async mode) → returns snapshot_id or None.
    #     """
    #     params = {
    #         "dataset_id":      dataset_id,
    #         "include_errors":  str(include_errors).lower(),
    #         "format":          "json",
    #         "sync_mode":       "async",
    #         **(extra_params or {}),
    #     }

    #     sent_at  = datetime.utcnow()
    #     trace_id = await self._next_trace_id()

    #     url = "https://api.brightdata.com/datasets/v3/trigger"
    #     headers = {
    #         "Authorization": f"Bearer {self._token}",
    #         "Content-Type":  "application/json",
    #     }

    #     # **new session per call**
    #     async with aiohttp.ClientSession(
    #         timeout=self._timeout,
    #         headers=headers,
    #         trust_env=True,
    #     ) as sess:
    #         try:
    #             async with sess.post(url, params=params, json=payload) as resp:
    #                 resp.raise_for_status()
    #                 data = await resp.json()
    #         except Exception as e:
    #             log.debug("trigger %s failed: %s", dataset_id, e)
    #             return None

    #     sid = data.get("snapshot_id")
    #     if not sid:
    #         log.debug("trigger response w/o snapshot_id: %s", data)
    #         return None

    #     # record metadata
    #     first_url      = payload[0].get("url", "") if payload else ""
    #     root_override  = tldextract.extract(first_url).domain or None
    #     BrightdataEngine._snap_meta[sid] = {
    #         "trace_id":                 trace_id,
    #         "request_sent_at":          sent_at,
    #         "snapshot_id_received_at":  datetime.utcnow(),
    #         "snapshot_polled_at":       [],
    #         "data_received_at":         None,
    #         "root_override":            root_override,
    #     }
    #     return sid

    async def get_status(self, snapshot_id: str) -> str:
        """
        One GET to /progress/{snapshot_id} → returns status string.
        """
        url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
        headers = {"Authorization": f"Bearer {self._token}"}

        async with aiohttp.ClientSession(
            timeout=self._timeout,
            headers=headers,
            trust_env=True,
        ) as sess:
            try:
                async with sess.get(url) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    status = data.get("status", "unknown").lower()
            except Exception as e:
                log.debug("status poll %s error: %s", snapshot_id, e)
                status = "error"

        BrightdataEngine._snap_meta.setdefault(snapshot_id, {}) \
                                  .setdefault("snapshot_polled_at", []) \
                                  .append(datetime.utcnow())
        return status
    

    async def fetch_result(self, snapshot_id: str) -> ScrapeResult:
        """
        GET /snapshot/{snapshot_id} and return a ScrapeResult.

        If the body still says {"status": "building"}, the request is retried
        every 2 s until real data arrives (or an HTTP/error response occurs).
        """
        url     = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json"
        headers = {"Authorization": f"Bearer {self._token}"}

        # ------------------------ download loop ------------------------
        while True:
            try:
                async with aiohttp.ClientSession(
                    timeout=self._timeout,
                    headers=headers,
                    trust_env=True,
                ) as sess:
                    async with sess.get(url) as resp:
                        resp.raise_for_status()
                        data = await resp.json()

                # Bright Data sometimes returns a placeholder:
                #   {"status":"building","message":"Snapshot is building …"}
                if isinstance(data, dict) and data.get("status") == "building":
                    await asyncio.sleep(2)        # short pause, then retry
                    continue

                ok, status, error = True, "ready", None
                BrightdataEngine._snap_meta[snapshot_id]["data_received_at"] = datetime.utcnow()
            except aiohttp.ClientResponseError as e:
                ok, status, error, data = False, "error", f"http_{e.status}", None
            except Exception as e:
                ok, status, error, data = False, "error", "fetch_error", None
                log.debug("fetch_result %s error: %s", snapshot_id, e)
            break   # leave retry-loop (success or hard error)

        # --------------------- derive counts & cost --------------------
        row_count   : Optional[int]   = None
        field_count : Optional[int]   = None
        cost        : Optional[float] = None

        if isinstance(data, list):
            row_count   = len(data)
            field_count = len(data[0]) if data and isinstance(data[0], dict) else 0
        elif isinstance(data, dict):
            row_count   = 1
            field_count = len(data)
        else:                       # unexpected data shape
            row_count   = 0
            field_count = 0

        if row_count is not None:
            cost = row_count * self.COST_PER_RECORD

        # -------------------------- package ---------------------------
        scrape_res = self._make_result(
            success       = ok,
            status        = status,
            snapshot_id   = snapshot_id,
            url           = url,
            data          = data,
            error         = error,
            cost          = cost,
            row_count     = row_count,
            field_count   = field_count,
        )
        return scrape_res
    
    # async def fetch_result(self, snapshot_id: str) -> ScrapeResult:
    #     """
    #     One GET to /snapshot/{snapshot_id} → returns a ScrapeResult.
    #     """
    #     url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json"
    #     headers = {"Authorization": f"Bearer {self._token}"}

    #     async with aiohttp.ClientSession(
    #         timeout=self._timeout,
    #         headers=headers,
    #         trust_env=True,
    #     ) as sess:
    #         try:
    #             async with sess.get(url) as resp:
    #                 resp.raise_for_status()
    #                 data = await resp.json()
    #             ok, status, error = True, "ready", None
    #             BrightdataEngine._snap_meta[snapshot_id]["data_received_at"] = datetime.utcnow()
    #         except aiohttp.ClientResponseError as e:
    #             ok, status, error, data = False, "error", f"http_{e.status}", None
    #         except Exception as e:
    #             ok, status, error, data = False, "error", "fetch_error", None
    #             log.debug("fetch_result %s error: %s", snapshot_id, e)

    #     cost: Optional[float] = None
    #     row_count: Optional[int] = None
    #     field_count: Optional[int] = None
        
        
    #     if isinstance(data, list):
    #         row_count = len(data)
    #         cost      = row_count * self.COST_PER_RECORD
    #         if data and isinstance(data[0], dict):
    #                 field_count = len(data[0])

    #     elif isinstance(data, dict):
    #         row_count = 1
    #         cost      = 1 * self.COST_PER_RECORD
    #         field_count = len(data)
    #     else:
    #         row_count = 0
    #         cost      = 0.0
    #         field_count = 0

    #     scrape_res =self._make_result(
    #         success=ok,
    #         status=status,
    #         snapshot_id=snapshot_id,
    #         url=url,
    #         data=data,
    #         error=error,
    #         cost=cost,
    #         row_count=row_count,
    #         field_count=field_count,
    #     )
    #     return scrape_res
    



    async def poll_until_ready(
        self,
        snapshot_id: str,
        *,
        poll_interval: int = 10,
        timeout: int = 600,
    ) -> ScrapeResult:
        """
        Async-block until ready or timeout, then return the final ScrapeResult.
        """
        start = time.time()
        while True:
            status = await self.get_status(snapshot_id)
            if status in {"ready", "error"}:
                scrape_res= await self.fetch_result(snapshot_id)
                return scrape_res

            if time.time() - start >= timeout:
                # give up
                return self._make_result(
                    success=False,
                    status="timeout",
                    snapshot_id=snapshot_id,
                    url=f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}",
                    error=f"gave up after {timeout}s",
                )
            await asyncio.sleep(poll_interval)

    def _make_result(
        self,
        *,
        success: bool,
        status: str,
        snapshot_id: str,
        url: str,
        data: Any = None,
        error: Optional[str] = None,
        cost: Optional[float]= None,
        row_count: Optional[int] = None,    # ← new
        field_count: Optional[int] = None, 
    ) -> ScrapeResult:
        meta = BrightdataEngine._snap_meta.get(snapshot_id, {})
        root = tldextract.extract(url).domain or None
        
        
        # handle Bright-Data disguise URLs
        if root == "brightdata":
            root = meta.get("root_override", root)
            if root == "brightdata" and (m := _BD_URL_RE.search(url)):
                decoded = urllib.parse.unquote(m.group(1))
                root = tldextract.extract(decoded).domain or root

        try:
            loop_id = id(asyncio.get_running_loop())
        except RuntimeError:
            loop_id = None

        return ScrapeResult(
            success=success,
            url=url,
            status=status,
            data=data,
            error=error,
            snapshot_id=snapshot_id,
            cost=cost,
            fallback_used=False,
            root_domain=root,
            event_loop_id=loop_id,
            request_sent_at=meta.get("request_sent_at"),
            snapshot_id_received_at=meta.get("snapshot_id_received_at"),
            snapshot_polled_at=meta.get("snapshot_polled_at", []),
            data_received_at=meta.get("data_received_at"),
            row_count=row_count, 
            field_count= field_count
        )


# convenience singleton
_engine: BrightdataEngine | None = None

def get_engine(token: Optional[str] = None) -> BrightdataEngine:
    """Return a singleton BrightdataEngine (per process)."""
    global _engine
    if _engine is None:
        _engine = BrightdataEngine(bearer_token=token)
    return _engine
