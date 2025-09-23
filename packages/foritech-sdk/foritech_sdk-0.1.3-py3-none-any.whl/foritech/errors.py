from __future__ import annotations

# Back-compat слой: `foritech.errors` огледално излага имената от `foritech.exceptions`
from .exceptions import (
    DecryptError,
    EncryptError,
    ForitechError,
    KeyLoadError,
    UnsupportedAlgorithm,
)

__all__ = [
    "ForitechError",
    "UnsupportedAlgorithm",
    "KeyLoadError",
    "EncryptError",
    "DecryptError",
]
