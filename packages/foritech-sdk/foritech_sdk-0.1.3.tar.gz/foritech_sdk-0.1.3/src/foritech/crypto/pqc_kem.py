# sdk/src/foritech/crypto/pqc_kem.py

from __future__ import annotations

import inspect
from typing import Tuple

__all__ = ["kem_selftest"]

def _oqs_import():
    """
    Ленива и безопасна импортация на oqs. Хвърля смислена грешка, ако липсва.
    """
    try:
        import oqs  # type: ignore
        return oqs
    except Exception as e:
        raise RuntimeError(
            "liboqs-python (oqs) не е намерен. Виж DEV-SETUP-OQS.md за инструкции."
        ) from e


def _kem_encap_decaps(kem, public_key: bytes) -> Tuple[bytes, bytes]:
    """
    Покрива и стария, и новия API на liboqs-python:
      – encapsulate(pk) / encap_secret(pk)
      – decap_secret(ct) / decap_secret(ct, sk)
    Връща (ss1, ss2).
    """
    # encapsulate
    if hasattr(kem, "encapsulate"):
        ct, ss1 = kem.encapsulate(public_key)
    else:
        ct, ss1 = kem.encap_secret(public_key)

    # decapsulate
    dec_sig = inspect.signature(kem.decap_secret)
    if len(dec_sig.parameters) == 1:           # (self, ct)
        ss2 = kem.decap_secret(ct)
    else:                                      # (self, ct, sk)
        ss2 = kem.decap_secret(ct, kem.export_secret_key())

    return ss1, ss2


def kem_selftest(alg: str = "Kyber768") -> Tuple[bool, int]:
    """
    Мини самодиагностика на KEM алгоритъм.
    Връща (ok, shared_secret_len). Ако ok=False, len=0.
    """
    oqs = _oqs_import()
    try:
        with oqs.KeyEncapsulation(alg) as kem:
            pk = kem.generate_keypair()  # само PK се връща (SK е вътре в обекта)
            ss1, ss2 = _kem_encap_decaps(kem, pk)
            ok = (ss1 == ss2) and (len(ss1) > 0)
            return ok, (len(ss1) if ok else 0)
    except Exception:
        return False, 0
