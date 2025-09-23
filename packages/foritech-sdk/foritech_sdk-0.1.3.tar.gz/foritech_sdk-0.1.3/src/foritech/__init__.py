from __future__ import annotations

import importlib
from typing import Any

# Back-compat: allow `from foritech import errors`
from . import errors  # noqa: F401

# Exceptions are always part of the public API
from .exceptions import (
    DecryptError,
    EncryptError,
    ForitechError,
    KeyLoadError,
    UnsupportedAlgorithm,
)

# Package version (from installed distribution name `foritech-sdk`)
try:
    from importlib.metadata import version as _pkg_version  # Python 3.8+
    __version__ = _pkg_version("foritech-sdk")
except Exception:  # dev/editable or not installed
    __version__ = "0.0.0"

# Optional facades (may be missing in lite builds). We avoid direct `from . import ...`
# to keep mypy happy and to not redefine module names.
def _opt_import(mod: str) -> Any | None:
    try:
        return importlib.import_module(__name__ + "." + mod)
    except Exception:
        return None

crypto: Any | None = _opt_import("crypto")
filecrypt: Any | None = _opt_import("filecrypt")
keygen: Any | None = _opt_import("keygen")

__all__ = [
    # Exceptions
    "ForitechError",
    "UnsupportedAlgorithm",
    "KeyLoadError",
    "EncryptError",
    "DecryptError",
    # Back-compat module
    "errors",
    # Version
    "__version__",
    # Optional facades
    "crypto",
    "filecrypt",
    "keygen",
]
