from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, List, Optional, AsyncIterator, TypedDict, Literal

import httpx


class APIError(Exception):
    """Raised when the server returns {"status": "ERR", ...} or a bad HTTP response."""
    def __init__(self, message: str, *, status: str = "ERR", payload: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status = status
        self.payload = payload or {}


Status = Literal["OK", "ERR"]


class _BaseResponse(TypedDict, total=False):
    status: Status
    message: str


class _RegisterServiceResponse(_BaseResponse, total=False):
    service_token: str


class _DeleteServiceResponse(_BaseResponse):
    pass


class _RootHashResponse(_BaseResponse, total=False):
    global_root: str


class _UpdateServiceResponse(_BaseResponse):
    pass


class _ListServicesResponse(_BaseResponse, total=False):
    services: List[Dict[str, str]]  # [{"service_name": "..."}]
    total: int
    has_more: bool
    next_page_id: Optional[int]


class _GetMyServicesResponse(_BaseResponse, total=False):
    services: List[Dict[str, Any]]  # [{"service_name": "...", "metadata": {...}}]


class _AddBlobResponse(_BaseResponse):
    pass


class _GetTokenResponse(_BaseResponse, total=False):
    token: str


class _UserAuthResponse(_BaseResponse):
    pass


class _CheckBlobResponse(_BaseResponse, total=False):
    bundle: Dict[str, Any]


class _HasServiceResponse(_BaseResponse):
    pass


class _GetServiceMetadataResponse(_BaseResponse, total=False):
    metadata: Dict[str, str]


@dataclass(frozen=True)
class ServiceInfo:
    service_name: str
    metadata: Optional[Dict[str, str]] = None


@dataclass(frozen=True)
class ListPage:
    services: List[ServiceInfo]
    total: int
    has_more: bool
    next_page_id: Optional[int]



def compute_blob_hash(data: bytes, digest_size: int = 8) -> str:
    """
    Compute a hex digest suitable for this API's 16-char requirement (default).
    The server expects `blob_hash` to be HEX and (by contract) length==16 chars,
    which corresponds to an 8-byte digest (16 hex chars).

    Use digest_size=8 (default) -> 16 hex chars.
    """
    if not (1 <= digest_size <= 64):
        raise ValueError("digest_size must be in [1, 64]")
    h = hashlib.blake2b(data, digest_size=digest_size)
    return h.hexdigest()


def _ensure_ok(payload: _BaseResponse) -> None:
    if payload.get("status") != "OK":
        # Prefer server message; fall back to a generic one
        raise APIError(payload.get("message") or "Server returned an error.", payload=payload)


def _coerce_services(items: Iterable[Dict[str, Any]]) -> List[ServiceInfo]:
    out: List[ServiceInfo] = []
    for it in items:
        name = it.get("service_name")
        if isinstance(name, str):
            md = it.get("metadata")
            name = name.replace("_", ".", 1)
            out.append(ServiceInfo(service_name=name, metadata=md if isinstance(md, dict) else None))
    return out


class _Core:
    """
    Common functionality for both sync and async clients.
    Do not instantiate directly. Use `CertumClient` (sync) or `AsyncCertumClient` (async).
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        if not base_url:
            raise ValueError("base_url must be a non-empty string")
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._headers = {"Content-Type": "application/json"}
        if headers:
            self._headers.update(headers)

    # ----------------- Endpoints -----------------

    # Auth / Users
    def _payload_user_login(self, username: str, password: str) -> Dict[str, Any]:
        return {"username": username, "password": password}

    def _payload_user_signup(self, username: str, password: str) -> Dict[str, Any]:
        return {"username": username, "password": password}

    # Services
    def _payload_register_service(self, service_name: str, username: str, password: str) -> Dict[str, Any]:
        return {"service_name": service_name, "username": username, "password": password}

    def _payload_delete_service(self, service_name: str, username: str, password: str) -> Dict[str, Any]:
        return {"service_name": service_name, "username": username, "password": password}

    def _payload_get_root_hash(self, service_name: str) -> Dict[str, Any]:
        return {"service_name": service_name}

    def _payload_update_service(self, service_name: str, username: str, password: str, metadata: Dict[str, str]) -> Dict[str, Any]:
        return {"service_name": service_name, "username": username, "password": password, "metadata": metadata}

    def _payload_list_services(self, username: str, filter_text: str, page_id: int, num_results: int) -> Dict[str, Any]:
        return {"username": username, "filter": filter_text, "page_id": page_id, "num_results": num_results}

    def _payload_get_my_services(self, username: str) -> Dict[str, Any]:
        return {"username": username}

    # Token & blobs
    def _payload_get_token(self, service_name: str, username: str, password: str) -> Dict[str, Any]:
        return {"service_name": service_name, "username": username, "password": password}

    def _payload_add_blob(self, service_name: str, token: str, blob_hash_hex16: str) -> Dict[str, Any]:
        return {"service_name": service_name, "token": token, "blob_hash": blob_hash_hex16}

    def _payload_check_blob(self, service_name: str, blob_hash_hex16: str) -> Dict[str, Any]:
        return {"service_name": service_name, "blob_hash": blob_hash_hex16}

    def _payload_has_service(self, service_name: str) -> Dict[str, Any]:
        return {"service_name": service_name}

    def _payload_get_service_metadata(self, service_name: str) -> Dict[str, Any]:
        return {"service_name": service_name}




class CertumClient(_Core):
    """
    Synchronous client. Usage:

        with CertumClient("http://localhost:8000") as c:
            c.user_signup("alice", "secret")
            ok = c.user_login("alice", "secret")

            token = c.register_service("notes", username="alice", password="secret")
            c.add_blob("alice.notes", token, compute_blob_hash(b"hello"))  # 16 hex chars
            root = c.get_root_hash("alice.notes")
    """

    def __init__(self, base_url: str, *, timeout: float = 10.0, headers: Optional[Dict[str, str]] = None) -> None:
        super().__init__(base_url, timeout=timeout, headers=headers)
        self._client = httpx.Client(base_url=self._base_url, timeout=self._timeout, headers=self._headers)

    # ---- lifecycle ----
    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "CertumClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    # ---- internal request ----
    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            r = self._client.post(path, content=json.dumps(payload))
        except Exception as e:
            raise APIError(f"Network error: {e}") from e

        if r.status_code != 200:
            raise APIError(f"HTTP {r.status_code}: {r.text[:200]}")

        try:
            data = r.json()
        except Exception as e:
            raise APIError(f"Invalid JSON response: {e}") from e

        return data

    # ---- public methods ----

    # Auth
    def user_login(self, username: str, password: str) -> bool:
        data: _UserAuthResponse = self._post("/user_login", self._payload_user_login(username, password))
        _ensure_ok(data)
        return True

    def user_signup(self, username: str, password: str) -> bool:
        data: _UserAuthResponse = self._post("/user_signup", self._payload_user_signup(username, password))
        _ensure_ok(data)
        return True

    # Services
    def register_service(self, service_name: str, username: str, password: str) -> str:
        data: _RegisterServiceResponse = self._post("/register_service", self._payload_register_service(service_name, username, password))
        _ensure_ok(data)
        token = data.get("service_token")
        if not isinstance(token, str):
            raise APIError("Malformed response: 'service_token' missing.")
        return token

    def delete_service(self, service_name: str, username: str, password: str) -> None:
        data: _DeleteServiceResponse = self._post("/delete_service", self._payload_delete_service(service_name, username, password))
        _ensure_ok(data)

    def get_root_hash(self, service_name: str) -> str:
        data: _RootHashResponse = self._post("/get_root_hash", self._payload_get_root_hash(service_name))
        _ensure_ok(data)
        rh = data.get("global_root")
        if not isinstance(rh, str):
            raise APIError("Malformed response: 'global_root' missing.")
        return rh

    def update_service(self, service_name: str, username: str, password: str, metadata: Dict[str, str]) -> bool:
        data: _UpdateServiceResponse = self._post("/update_service", self._payload_update_service(service_name, username, password, metadata))
        _ensure_ok(data)
        return True

    def list_services(self, username: str, *, filter_text: str = "", page_id: int = 1, num_results: int = 50) -> ListPage:
        data: _ListServicesResponse = self._post("/list_services", self._payload_list_services(username, filter_text, page_id, num_results))
        _ensure_ok(data)
        services_raw = data.get("services", [])
        total = int(data.get("total", 0))
        has_more = bool(data.get("has_more", False))
        next_page_id = data.get("next_page_id")
        return ListPage(services=_coerce_services(services_raw), total=total, has_more=has_more, next_page_id=next_page_id)

    def iter_services(self, username: str, *, filter_text: str = "", per_page: int = 50) -> Iterator[ServiceInfo]:
        page = 1
        while True:
            lp = self.list_services(username, filter_text=filter_text, page_id=page, num_results=per_page)
            for s in lp.services:
                yield s
            if not lp.has_more or not lp.next_page_id:
                break
            page = lp.next_page_id

    def get_my_services(self, username: str) -> List[ServiceInfo]:
        data: _GetMyServicesResponse = self._post("/get_my_services", self._payload_get_my_services(username))
        _ensure_ok(data)
        return _coerce_services(data.get("services", []))

    # Tokens & blobs
    def get_token(self, service_name: str, username: str, password: str) -> str:
        data: _GetTokenResponse = self._post("/get_token", self._payload_get_token(service_name, username, password))
        _ensure_ok(data)
        tok = data.get("token")
        if not isinstance(tok, str) or not tok:
            raise APIError("Malformed response: 'token' missing.")
        return tok

    def add_blob(self, service_name: str, token: str, blob_hash_hex16: str) -> None:
        if not (isinstance(blob_hash_hex16, str) and len(blob_hash_hex16) == 16):
            raise ValueError("blob_hash must be a 16-hex-character string (8 bytes).")
        data: _AddBlobResponse = self._post("/add_blob", self._payload_add_blob(service_name, token, blob_hash_hex16))
        _ensure_ok(data)

    def check_blob(self, service_name: str, blob_hash_hex16: str) -> Dict[str, Any]:
        if not (isinstance(blob_hash_hex16, str) and len(blob_hash_hex16) == 16):
            raise ValueError("blob_hash must be a 16-hex-character string (8 bytes).")
        data: _CheckBlobResponse = self._post("/check_blob", self._payload_check_blob(service_name, blob_hash_hex16))
        _ensure_ok(data)
        bundle = data.get("bundle")
        if not isinstance(bundle, dict):
            raise APIError("Malformed response: 'bundle' missing.")
        return bundle

    def has_service(self, service_name: str) -> bool:
        data: _HasServiceResponse = self._post("/has_service", self._payload_has_service(service_name))
        # Note: endpoint returns ERR if service doesn't exist; OK otherwise.
        return data.get("status") == "OK"

    def get_service_metadata(self, service_name: str) -> Dict[str, str]:
        data: _GetServiceMetadataResponse = self._post("/get_service_metadata", self._payload_get_service_metadata(service_name))
        _ensure_ok(data)
        md = data.get("metadata")
        if not isinstance(md, dict):
            raise APIError("Malformed response: 'metadata' missing.")
        # Ensure keys/values are strings
        return {str(k): str(v) for k, v in md.items()}



class AsyncCertumClient(_Core):
    """
    Asynchronous client. Usage:

        async with AsyncCertumClient("http://localhost:8000") as c:
            await c.user_signup("alice", "secret")
            await c.user_login("alice", "secret")

            token = await c.register_service("notes", username="alice", password="secret")
            await c.add_blob("alice.notes", token, compute_blob_hash(b"hello"))
            root = await c.get_root_hash("alice.notes")
    """

    def __init__(self, base_url: str, *, timeout: float = 10.0, headers: Optional[Dict[str, str]] = None) -> None:
        super().__init__(base_url, timeout=timeout, headers=headers)
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout, headers=self._headers)

    # ---- lifecycle ----
    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncCertumClient":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()

    # ---- internal request ----
    async def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            r = await self._client.post(path, content=json.dumps(payload))
        except Exception as e:
            raise APIError(f"Network error: {e}") from e

        if r.status_code != 200:
            raise APIError(f"HTTP {r.status_code}: {r.text[:200]}")

        try:
            data = r.json()
        except Exception as e:
            raise APIError(f"Invalid JSON response: {e}") from e

        return data

    # ---- public methods (async) ----

    # Auth
    async def user_login(self, username: str, password: str) -> bool:
        data: _UserAuthResponse = await self._post("/user_login", self._payload_user_login(username, password))
        _ensure_ok(data)
        return True

    async def user_signup(self, username: str, password: str) -> bool:
        data: _UserAuthResponse = await self._post("/user_signup", self._payload_user_signup(username, password))
        _ensure_ok(data)
        return True

    # Services
    async def register_service(self, service_name: str, username: str, password: str) -> str:
        data: _RegisterServiceResponse = await self._post("/register_service", self._payload_register_service(service_name, username, password))
        _ensure_ok(data)
        token = data.get("service_token")
        if not isinstance(token, str):
            raise APIError("Malformed response: 'service_token' missing.")
        return token

    async def delete_service(self, service_name: str, username: str, password: str) -> None:
        data: _DeleteServiceResponse = await self._post("/delete_service", self._payload_delete_service(service_name, username, password))
        _ensure_ok(data)

    async def get_root_hash(self, service_name: str) -> str:
        data: _RootHashResponse = await self._post("/get_root_hash", self._payload_get_root_hash(service_name))
        _ensure_ok(data)
        rh = data.get("global_root")
        if not isinstance(rh, str):
            raise APIError("Malformed response: 'global_root' missing.")
        return rh

    async def update_service(self, service_name: str, username: str, password: str, metadata: Dict[str, str]) -> bool:
        data: _UpdateServiceResponse = await self._post("/update_service", self._payload_update_service(service_name, username, password, metadata))
        _ensure_ok(data)
        return True

    async def list_services(self, username: str, *, filter_text: str = "", page_id: int = 1, num_results: int = 50) -> ListPage:
        data: _ListServicesResponse = await self._post("/list_services", self._payload_list_services(username, filter_text, page_id, num_results))
        _ensure_ok(data)
        services_raw = data.get("services", [])
        total = int(data.get("total", 0))
        has_more = bool(data.get("has_more", False))
        next_page_id = data.get("next_page_id")
        return ListPage(services=_coerce_services(services_raw), total=total, has_more=has_more, next_page_id=next_page_id)

    async def iter_services(self, username: str, *, filter_text: str = "", per_page: int = 50) -> AsyncIterator[ServiceInfo]:
        page = 1
        while True:
            lp = await self.list_services(username, filter_text=filter_text, page_id=page, num_results=per_page)
            for s in lp.services:
                yield s
            if not lp.has_more or not lp.next_page_id:
                break
            page = lp.next_page_id

    async def get_my_services(self, username: str) -> List[ServiceInfo]:
        data: _GetMyServicesResponse = await self._post("/get_my_services", self._payload_get_my_services(username))
        _ensure_ok(data)
        return _coerce_services(data.get("services", []))

    # Tokens & blobs
    async def get_token(self, service_name: str, username: str, password: str) -> str:
        data: _GetTokenResponse = await self._post("/get_token", self._payload_get_token(service_name, username, password))
        _ensure_ok(data)
        tok = data.get("token")
        if not isinstance(tok, str) or not tok:
            raise APIError("Malformed response: 'token' missing.")
        return tok

    async def add_blob(self, service_name: str, token: str, blob_hash_hex16: str) -> None:
        if not (isinstance(blob_hash_hex16, str) and len(blob_hash_hex16) == 16):
            raise ValueError("blob_hash must be a 16-hex-character string (8 bytes).")
        data: _AddBlobResponse = await self._post("/add_blob", self._payload_add_blob(service_name, token, blob_hash_hex16))
        _ensure_ok(data)

    async def check_blob(self, service_name: str, blob_hash_hex16: str) -> Dict[str, Any]:
        if not (isinstance(blob_hash_hex16, str) and len(blob_hash_hex16) == 16):
            raise ValueError("blob_hash must be a 16-hex-character string (8 bytes).")
        data: _CheckBlobResponse = await self._post("/check_blob", self._payload_check_blob(service_name, blob_hash_hex16))
        _ensure_ok(data)
        bundle = data.get("bundle")
        if not isinstance(bundle, dict):
            raise APIError("Malformed response: 'bundle' missing.")
        return bundle

    async def has_service(self, service_name: str) -> bool:
        data: _HasServiceResponse = await self._post("/has_service", self._payload_has_service(service_name))
        return data.get("status") == "OK"

    async def get_service_metadata(self, service_name: str) -> Dict[str, str]:
        data: _GetServiceMetadataResponse = await self._post("/get_service_metadata", self._payload_get_service_metadata(service_name))
        _ensure_ok(data)
        md = data.get("metadata")
        if not isinstance(md, dict):
            raise APIError("Malformed response: 'metadata' missing.")
        return {str(k): str(v) for k, v in md.items()}