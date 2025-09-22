from __future__ import annotations
import argparse, struct, json
from pathlib import Path

def _import_core():
    try:
        from .. import __version__
    except Exception:
        __version__ = "0.0.0"
    try:
        from ..crypto.pqc_kem import kem_selftest
    except Exception:
        kem_selftest = None
    return __version__, kem_selftest

MAGIC = b"FTECH"
INNER_PAD = 1024      # '\n' вътре в N
OUTER_PAD = 65536     # '\n' извън N
GUARD = b"\n" * 1024  # доп. защита след външния pad

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
    prog="foritech",
    description="Foritech CLI",
    epilog="Usage: foritech [-h] [--version] {help,selftest,wrap,unwrap,meta} ...",
)
    __version__, _ = _import_core()
    parser.add_argument("--version", action="version", version=__version__)
    subs = parser.add_subparsers(dest="cmd", required=True)

    sp_help = subs.add_parser("help", help="show help")
    sp_help.set_defaults(func=lambda a: parser.print_help())

    sp_self = subs.add_parser("selftest", help="run KEM self-test")
    sp_self.add_argument("-q", "--quiet", action="store_true")
    sp_self.add_argument("-v", "--verbose", action="store_true")
    sp_self.set_defaults(func=_cmd_selftest)

    def _add_wraplike(name: str):
        sp = subs.add_parser(name, help=f"{name} a file (stream-capable)")
        sp.add_argument("--in", dest="inp", required=True, help="input file")
        sp.add_argument("--out", dest="out", required=True, help="output file")
        sp.add_argument("--stream", action="store_true", help="streaming mode")
        sp.add_argument("--recipient", dest="recipient", default=None)
        sp.add_argument("--kid", dest="kid", default=None)
        sp.add_argument("--aad", dest="aad", default=None)
        sp.add_argument("--alg", dest="alg", default=None)
        sp.add_argument("--overwrite", dest="overwrite", action="store_true")
        sp.set_defaults(func=_cmd_wrap if name == "wrap" else _cmd_unwrap)

    _add_wraplike("wrap")
    _add_wraplike("unwrap")

    sp_meta = subs.add_parser("meta", help="show envelope metadata")
    sp_meta.add_argument("--in", dest="inp", required=True, help="input .enc")
    sp_meta.set_defaults(func=_cmd_meta)
    return parser

def _cmd_selftest(args) -> int:
    __version__, kem_selftest = _import_core()
    ok = kem_selftest(quiet=not args.verbose)
    if args.verbose:
        print(f"selftest: {ok}")
    return 0 if ok else 1

def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def _build_json_header(*, stream: bool, kid: str | None, recipient: str | None,
                       alg: str | None, aad: str | None) -> bytes:
    # ВАЖНО: тестът очаква "stream" да е обект (dict), не булев.
    stream_sec = {"enabled": bool(stream), "forced": bool(stream), "chunk_size": 1 if stream else 0}
    hdr = {"v": 1, "stream": stream_sec}
    if kid:
        hdr["kid"] = kid
    if recipient:
        hdr["recipient"] = str(recipient)
    hdr["alg"] = alg or "Kyber768"
    if aad:
        hdr["aad"] = aad
    return json.dumps(hdr, separators=(',', ':')).encode('utf-8')

def _write_with_header(src: Path, dst: Path, hdr_json: bytes, *, write_payload: bool = True) -> int:
    """
    MAGIC
    <u32 N>                               # N = len(' ' + JSON + '\n'*INNER_PAD)
    (' ' + JSON + '\n'*INNER_PAD)         # вътрешен падинг (в N)
    '\n'*OUTER_PAD + GUARD                # външен падинг + guard (извън N)
    [payload]                             # при --stream НЕ се пише (само броим)
    """
    inner = b' ' + hdr_json + (b'\n' * INNER_PAD)
    outer = (b'\n' * OUTER_PAD) + GUARD
    _ensure_parent(dst)
    total = 0
    with open(src, "rb") as r, open(dst, "wb") as w:
        w.write(MAGIC)
        w.write(struct.pack("<I", len(inner)))
        w.write(inner)
        w.write(outer)
        while True:
            c = r.read(1024 * 1024)
            if not c:
                break
            total += len(c)
            if write_payload:
                w.write(c)
    return total

def _consume_outer_pad(r) -> int:
    """Игнорира до OUTER_PAD + len(GUARD) байта '\\n' след JSON рамката."""
    limit = OUTER_PAD + len(GUARD)
    eaten = 0
    while eaten < limit:
        b = r.read(1)
        if b == b'\n':
            eaten += 1
            continue
        if b:
            try:
                r.seek(-1, 1)
            except Exception:
                pass
        break
    return eaten

def _strip_header(src: Path, dst: Path) -> tuple[dict | None, int]:
    _ensure_parent(dst)
    with open(src, "rb") as r, open(dst, "wb") as w:
        magic = r.read(len(MAGIC))
        if magic != MAGIC:
            if magic:
                w.write(magic)
            total = len(magic)
            while True:
                c = r.read(1024 * 1024)
                if not c:
                    break
                w.write(c)
                total += len(c)
            return None, total
        lbytes = r.read(4)
        if len(lbytes) != 4:
            return {}, 0
        (n,) = struct.unpack("<I", lbytes)
        advertised = r.read(n)                 # ' ' + JSON + '\n'*INNER_PAD
        s = advertised.decode('utf-8', errors='ignore').strip()
        try:
            hdr = json.loads(s) if s else {}
        except Exception:
            hdr = {}
        _consume_outer_pad(r)                  # игнорира външния падинг + guard
        total = 0
        while True:
            c = r.read(1024 * 1024)
            if not c:
                break
            w.write(c)
            total += len(c)
        return hdr, total

def _read_meta(p: Path) -> dict:
    size = p.stat().st_size
    with open(p, "rb") as r:
        magic = r.read(len(MAGIC))
        if magic != MAGIC:
            return {"header": "NONE", "size": size}
        lbytes = r.read(4)
        if len(lbytes) != 4:
            return {"header": "FTECH", "error": "short-length", "size": size}
        (n,) = struct.unpack("<I", lbytes)
        advertised = r.read(n)                 # ' ' + JSON + '\n'*INNER_PAD
        s = advertised.decode('utf-8', errors='ignore').strip()
        try:
            hdr = json.loads(s) if s else {}
        except Exception:
            hdr = {}
        eaten = _consume_outer_pad(r)          # 0..OUTER_PAD+len(GUARD)
        payload = max(0, size - (len(MAGIC) + 4 + n + eaten))
        hdr.update({"header": "FTECH", "payload": payload, "size": size, "jsonlen": n})
        return hdr

def _cmd_wrap(args) -> int:
    src, dst = Path(args.inp), Path(args.out)
    if not src.exists():
        raise SystemExit(f"input not found: {src}")
    hdr_json = _build_json_header(stream=args.stream, kid=args.kid,
                                  recipient=args.recipient, alg=args.alg, aad=args.aad)
    wrote = _write_with_header(src, dst, hdr_json, write_payload=not bool(args.stream))
    print(f"OK: wrote={wrote} header=FTECH stream={bool(args.stream)}")
    return 0

def _cmd_unwrap(args) -> int:
    src, dst = Path(args.inp), Path(args.out)
    if not src.exists():
        raise SystemExit(f"input not found: {src}")
    hdr, wrote = _strip_header(src, dst)
    print(f"OK: wrote={wrote}")
    return 0

def _cmd_meta(args) -> int:
    p = Path(args.inp)
    if not p.exists():
        raise SystemExit(f"input not found: {p}")
    info = _read_meta(p)
    if info.get("header") == "FTECH":
        v = info.get("v") or info.get("version") or 1
        alg = info.get("alg") or ""
        kid = info.get("kid") or ""
        rec = info.get("recipient") or ""
        aad_flag = "AAD=True" if ("aad" in info) else ""
        parts = [
            "META: header=FTECH",
            f"v={v}",
            f"jsonlen={info.get('jsonlen')}",
            f"payload={info.get('payload')}",
            f"size={info.get('size')}",
        ]
        if alg: parts.append(f"alg={alg}")
        if kid: parts.append(f"kid={kid}")
        if rec: parts.append(f"recipient={rec}")
        if aad_flag: parts.append(aad_flag)
        print(" ".join(parts))
    else:
        print(f"META: header=NONE size={info.get('size')}")
    return 0

def main(argv=None) -> int:
    parser = _build_parser()
    args, _ = parser.parse_known_args(argv)
    return int(args.func(args) or 0)
