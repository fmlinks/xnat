from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class XnatClient:
    base_url: str
    project: str
    alias: str
    secret: str
    verify_tls: bool = True

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        self._session = requests.Session()
        self._session.auth = (self.alias, self.secret)
        self._session.verify = self.verify_tls

        retry_kwargs = dict(
            total=5,
            backoff_factor=0.8,
            status_forcelist=(429, 500, 502, 503, 504),
            raise_on_status=False,
        )
        try:
            retry = Retry(**retry_kwargs, allowed_methods=frozenset(["GET", "PUT", "POST", "DELETE", "HEAD", "OPTIONS"]))
        except TypeError:
            retry = Retry(**retry_kwargs, method_whitelist=frozenset(["GET", "PUT", "POST", "DELETE", "HEAD", "OPTIONS"]))

        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def _check_ok(self, resp: requests.Response) -> None:
        if 200 <= resp.status_code < 300:
            return
        txt = resp.text or ""
        txt = txt[:2000] + ("\n...[truncated]..." if len(txt) > 2000 else "")
        raise RuntimeError(
            f"Request failed\n"
            f"  {resp.request.method} {resp.url}\n"
            f"  HTTP {resp.status_code}\n"
            f"{txt}"
        )

    def url(self, path: str) -> str:
        if path.startswith("/"):
            return f"{self.base_url}{path}"
        return f"{self.base_url}/{path}"

    def get_json(self, path: str, timeout: int = 60) -> Dict[str, Any]:
        r = self._session.get(self.url(path), timeout=timeout)
        self._check_ok(r)
        return r.json()

    def put_empty(self, path: str, params: Optional[Dict[str, Any]] = None, timeout: int = 60) -> None:
        r = self._session.put(self.url(path), params=params, timeout=timeout)
        self._check_ok(r)

    def put_file(self, path: str, local_path: str, params: Optional[Dict[str, Any]] = None, timeout: int = 600) -> None:
        headers = {"Content-Type": "application/octet-stream"}
        with open(local_path, "rb") as f:
            r = self._session.put(self.url(path), params=params, data=f, headers=headers, timeout=timeout)
        self._check_ok(r)

    def smoke_test_project_access(self) -> None:
        _ = self.get_json(f"/data/projects/{self.project}?format=json")
