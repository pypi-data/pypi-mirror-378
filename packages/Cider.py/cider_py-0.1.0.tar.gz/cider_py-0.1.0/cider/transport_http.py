from typing import Any, Dict, Optional
import requests
import httpx
from .exceptions import AuthenticationError, ConnectionError, APIServerError

class SyncHTTP:
    def __init__(self, base_url: str, api_token: Optional[str] = None, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.timeout = timeout
        self.api_token = api_token

    def _headers(self) -> Dict[str, str]:
        h = {"Accept": "application/json"}
        if self.api_token:
            h["apitoken"] = self.api_token
        return h

    def get(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            r = self.session.get(url, headers=self._headers(), timeout=self.timeout)
        except requests.RequestException as e:
            raise ConnectionError(str(e))
        if r.status_code == 401:
            raise AuthenticationError("Unauthorized: API token required or invalid")
        if r.status_code == 204:
            return {"status": "ok", "no_content": True}
        if r.status_code >= 400:
            raise APIServerError(f"HTTP {r.status_code}: {r.text}")
        if r.content:
            return r.json()
        return {"status": "ok"}

    def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            r = self.session.post(url, json=json or {}, headers=self._headers(), timeout=self.timeout)
        except requests.RequestException as e:
            raise ConnectionError(str(e))
        if r.status_code == 401:
            raise AuthenticationError("Unauthorized: API token required or invalid")
        if r.status_code == 204:
            return {"status": "ok", "no_content": True}
        if r.status_code >= 400:
            raise APIServerError(f"HTTP {r.status_code}: {r.text}")
        if r.content:
            return r.json()
        return {"status": "ok"}


class AsyncHTTP:
    def __init__(self, base_url: str, api_token: Optional[str] = None, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=timeout)
        self.api_token = api_token

    def _headers(self) -> Dict[str, str]:
        h = {"Accept": "application/json"}
        if self.api_token:
            h["apitoken"] = self.api_token
        return h

    async def get(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            r = await self.client.get(url, headers=self._headers())
        except httpx.HTTPError as e:
            raise ConnectionError(str(e))
        if r.status_code == 401:
            raise AuthenticationError("Unauthorized: API token required or invalid")
        if r.status_code == 204:
            return {"status": "ok", "no_content": True}
        if r.status_code >= 400:
            raise APIServerError(f"HTTP {r.status_code}: {r.text}")
        if r.content:
            return r.json()
        return {"status": "ok"}

    async def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            r = await self.client.post(url, json=json or {}, headers=self._headers())
        except httpx.HTTPError as e:
            raise ConnectionError(str(e))
        if r.status_code == 401:
            raise AuthenticationError("Unauthorized: API token required or invalid")
        if r.status_code == 204:
            return {"status": "ok", "no_content": True}
        if r.status_code >= 400:
            raise APIServerError(f"HTTP {r.status_code}: {r.text}")
        if r.content:
            return r.json()
        return {"status": "ok"}

    async def aclose(self):
        await self.client.aclose()
