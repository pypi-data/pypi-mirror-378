from __future__ import annotations

import requests
from datetime import datetime
from typing import Optional, Any, Dict, Mapping, MutableMapping, Protocol, TypeVar, Union, overload
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

DEFAULT_BASE_URL = "https://api.cronpulse.com"  # TODO: confirm actual production URL

JSONPrimitive = Union[str, int, float, bool, None]
JSONType = Union[JSONPrimitive, "JSONDict", list[JSONPrimitive]]
class JSONDict(Dict[str, JSONType]):
    """Typed JSON mapping helper (narrow enough for our payloads)."""
    pass

TMonitor = TypeVar("TMonitor", bound="Monitor")

class CronPulse:
    """CronPulse API client.

    Provides helper methods to create and work with Monitors. A resilient
    `requests.Session` with retries is used for idempotent operations.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 10.0,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

        # Build a Session with retry for transient errors (5xx + 429)
        self._session = requests.Session()
        retry = Retry(
            total=max_retries,
            status=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST", "DELETE", "PUT", "PATCH"),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    # ---- internal helpers ----
    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Mapping[str, Any]] = None,
    ) -> requests.Response:
        url = f"{self.base_url}{path}" if path.startswith('/') else f"{self.base_url}/{path}"
        resp = self._session.request(
            method,
            url,
            json=dict(json) if json is not None else None,  # copy to avoid caller mutation side-effects
            headers=self._headers(),
            timeout=self.timeout,
        )
        # Raise for client errors (4xx) & server (5xx) after retries
        resp.raise_for_status()
        return resp

    # ---- public API ----
    def create_monitor(
        self,
        name: str,
        interval: int,
        email: str,
        expires_at: datetime,
    ) -> "Monitor":
        payload = {
            "name": name,
            "interval": interval,
            "email": email,
            "expires_at": expires_at.isoformat(),
        }
        resp = self._request("POST", "/monitors", json=payload)
        data = resp.json()
        monitor_id = str(data["id"])  # ensure string
        return Monitor(monitor_id, client=self)

class Monitor:
    """Represents a created monitor resource."""

    def __init__(self, monitor_id: str, client: CronPulse):
        self.monitor_id = monitor_id
        self._client = client

    @property
    def api_key(self) -> str:  # pragma: no cover - trivial
        return self._client.api_key

    @property
    def base_url(self) -> str:  # pragma: no cover - trivial
        return self._client.base_url

    def ping(self) -> None:
        self._client._request("POST", f"/monitors/{self.monitor_id}/ping")

    def delete(self) -> None:
        self._client._request("DELETE", f"/monitors/{self.monitor_id}")
