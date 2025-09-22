from __future__ import annotations

# Public API
from .client import (
    CertumClient,
    AsyncCertumClient,
    APIError,
    ServiceInfo,
    ListPage,
    compute_blob_hash,
)

# Expose package version (best-effort)
try:
    from importlib.metadata import version, PackageNotFoundError  # py3.8+
except Exception:  # pragma: no cover
    version = None
    PackageNotFoundError = Exception  # type: ignore[misc]

__all__ = [
    "CertumClient",
    "AsyncCertumClient",
    "APIError",
    "ServiceInfo",
    "ListPage",
    "compute_blob_hash",
    "__version__",
]

def _get_version() -> str:
    if version is None:
        return "0"
    try:
        return version("certum_client")
    except Exception:
        return "0"

__version__ = _get_version()