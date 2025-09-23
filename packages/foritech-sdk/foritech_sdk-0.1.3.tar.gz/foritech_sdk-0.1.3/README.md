# Foritech SDK
Локален README за Python пакета. За пълна документация виж ../README.md.
# Foritech SDK

Python SDK for Foritech Secure System.

# Foritech SDK (Python)

Лек Python SDK за пост-квантова криптография (Kyber768/ML-KEM) и базови операции за ключове и файлово шифриране. Работи самостоятелно (Python) и/или чрез Docker-базирания CLI wrapper.

> PyPI пакет: **foritech-sdk** • Лиценз: MIT • Поддържани Python: 3.11, 3.12, 3.13

---

## Quickstart (60 секунди)

```bash
# 1) Инсталиране
pip install -U foritech-sdk

# 2) Минимален пример (encrypt/decrypt)
python - << 'PY'
from foritech import crypto  # пример: модулът ви може да е foritech.crypto

data = b"hello post-quantum world"
aad  = b"example-aad"

ct = crypto.encrypt(data, aad=aad)     # връща {ciphertext, key/nonce/...} или bytes според API
pt = crypto.decrypt(ct, aad=aad)

assert pt == data
print("OK: encrypt/decrypt")
PY

# Foritech CLI Wrapper A — Implementation Pack

This package provides everything you asked for to implement Variant A (Docker-based CLI wrapper), plus the sync note for Variant B. Copy/paste files as indicated.

---

## 0) File tree (new/updated)

```
repo-root/
├─ sdk/
│  ├─ pyproject.toml                 # + console_scripts entry (update)
│  └─ src/
│     └─ foritech_cli/
│        ├─ __init__.py
│        └─ main.py                  # wrapper entrypoint (argparse)
├─ docs/
│  └─ CLI_WRAPPER_SYNC.md            # note: how to keep A in sync with B
├─ examples/
│  ├─ 01_keygen.sh                   # example using wrapper A
│  ├─ 02_encrypt_file.sh
│  └─ 03_decrypt_file.sh
├─ sdk/tests/
│  └─ test_cli_wrapper_smoke.py      # pytest: skipped if no docker
├─ .github/workflows/
│  └─ cli-wrapper-smoke.yml          # CI smoke job (Ubuntu)
└─ README.md                         # add short “CLI (Wrapper)” section (update)
```

> If your SDK code lives under a different subpackage root, adjust imports/paths accordingly.

---

## 1) sdk/src/foritech_cli/__init__.py

```python
__all__ = ["main"]
from .main import main  # re-export for console_scripts hook
```

---

## 2) sdk/src/foritech_cli/main.py (Docker wrapper)

```python
import argparse
import os
import shutil
import subprocess
import sys
from typing import List

# Pin your canonical image here. Replace the digest with your current published image digest.
# You can also read it from an env var (FORITECH_IMAGE) with this as default.
DEFAULT_IMAGE = os.environ.get(
    "FORITECH_IMAGE",
    "ghcr.io/foritech-secure-system/foritech:stable@sha256:YOUR_PINNED_DIGEST_HERE",
)

# Common Docker args. We run as current user where possible to avoid root-owned outputs on Linux.
# On macOS/Windows this just works; on Linux it avoids permission issues.

def _docker_base_args() -> List[str]:
    args = [
        "docker",
        "run",
        "--rm",
        "-i",
    ]

    # Mount current working directory into /work (read-write)
    cwd = os.getcwd()
    args += ["-v", f"{cwd}:/work"]

    # Propagate UID/GID on Linux to avoid root-owned output files
    if os.name == "posix":
        try:
            uid = os.getuid()
            gid = os.getgid()
            args += ["-u", f"{uid}:{gid}"]
        except AttributeError:
            pass

    # Set working dir inside container
    args += ["-w", "/work"]

    # Pass through basic envs if set (helpful for non-interactive CI)
    for env_name in ("TZ", "FORITECH_LOGLEVEL"):
        if env_name in os.environ:
            args += ["-e", f"{env_name}={os.environ[env_name]}"]

    return args


def _ensure_docker_available() -> None:
    if not shutil.which("docker"):
        print("Error: Docker is not installed or not in PATH.", file=sys.stderr)
        sys.exit(127)


def run_container(image: str, inner_args: List[str]) -> int:
    """Run Docker with the given image and inner CLI args. Return the exit code."""
    cmd = _docker_base_args() + [image] + inner_args
    try:
        proc = subprocess.run(cmd, check=False)
        return proc.returncode
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        print(f"Runtime error: {e}", file=sys.stderr)
        return 2


def main(argv: List[str] | None = None) -> int:
    _ensure_docker_available()

    parser = argparse.ArgumentParser(
        prog="foritech",
        description="Foritech CLI (Docker wrapper). This mirrors the real Python CLI (when available).",
    )

    parser.add_argument(
        "--image",
        default=DEFAULT_IMAGE,
        help="Docker image to use (pinned digest recommended). Can also set FORITECH_IMAGE env.",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # foritech keygen --alg Kyber768 --out key.bin (example)
    p_keygen = sub.add_parser("keygen", help="Generate Kyber768 keypair or KEM material.")
    p_keygen.add_argument("--alg", default="Kyber768", help="Algorithm (default: Kyber768)")
    p_keygen.add_argument("--out", required=True, help="Output path for generated key material")

    # foritech encrypt --in file --out file.enc --aad optional
    p_encrypt = sub.add_parser("encrypt", help="Encrypt file with SDK defaults.")
    p_encrypt.add_argument("--in", dest="in_path", required=True, help="Input file")
    p_encrypt.add_argument("--out", dest="out_path", required=True, help="Output file")
    p_encrypt.add_argument("--aad", dest="aad", default=None, help="Additional authenticated data (optional)")

    # foritech decrypt --in file.enc --out file
    p_decrypt = sub.add_parser("decrypt", help="Decrypt file with SDK defaults.")
    p_decrypt.add_argument("--in", dest="in_path", required=True, help="Input file")
    p_decrypt.add_argument("--out", dest="out_path", required=True, help="Output file")
    p_decrypt.add_argument("--aad", dest="aad", default=None, help="Aad value if used on encrypt (optional)")

    # passthrough: forward unknown commands to the Docker CLI inside (advanced usage)
    p_raw = sub.add_parser("raw", help="Pass through arguments directly to container CLI.")
    p_raw.add_argument("args", nargs=argparse.REMAINDER, help="Arguments passed as-is to container")

    args = parser.parse_args(argv)

    # Map subcommands to inner container CLI invocations.
    # Replace the inner command below with the actual CLI inside your Docker image.
    # Example assumes your container exposes `foritech-cli` with similar verbs.

    inner_cmd = ["foritech-cli"]

    if args.command == "keygen":
        inner = inner_cmd + [
            "keygen",
            "--alg", args.alg,
            "--out", args.out,
        ]
        return run_container(args.image, inner)

    if args.command == "encrypt":
        inner = inner_cmd + [
            "encrypt",
            "--in", args.in_path,
            "--out", args.out_path,
        ]
        if args.aad:
            inner += ["--aad", args.aad]
        return run_container(args.image, inner)

    if args.command == "decrypt":
        inner = inner_cmd + [
            "decrypt",
            "--in", args.in_path,
            "--out", args.out_path,
        ]
        if args.aad:
            inner += ["--aad", args.aad]
        return run_container(args.image, inner)

    if args.command == "raw":
        # Pass everything after 'raw' directly
        return run_container(args.image, inner_cmd + args.args)

    # Should not reach here
    parser.print_usage(sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

> Replace `foritech-cli` in `inner_cmd` with the actual command available inside your Docker image. Keep verbs (`keygen/encrypt/decrypt`) identical to what Variant B will provide.

---

## 3) sdk/pyproject.toml (snippet to add console script)

```toml
[project.scripts]
foritech = "foritech_cli.main:main"
```

> Place this under the `sdk/pyproject.toml` `[project.scripts]` table. If a scripts table already exists, merge the entry.

---

## 4) docs/CLI_WRAPPER_SYNC.md (sync note A ↔ B)

```markdown
# CLI Wrapper A ↔ Python CLI B: Sync Note

**Purpose**: Wrapper A mirrors the future real Python CLI (Variant B). Whenever B changes, update A accordingly.

**Checklist on every B change:**
1. **Subcommands & names** — keep identical verbs (`keygen`, `encrypt`, `decrypt`).
2. **Flags & defaults** — reflect new/changed flags; sync default values.
3. **I/O formats** — keep output format/paths consistent; update examples.
4. **Errors & exit codes** — map exceptions to the same process codes.
5. **Logging levels** — align `--quiet/--verbose` semantics.
6. **Version/help** — `--version`/`--help` text and epigraph must match.
7. **Docs/CI** — update README examples and smoke tests as needed.
```

---

## 5) README.md (add short Wrapper section)

```markdown
## CLI (Wrapper A)

The `foritech` command is a thin Docker-based wrapper that mirrors the upcoming native Python CLI. Requirements: Docker. You can override the image via `FORITECH_IMAGE` env or `--image` flag.

Quickstart:

```bash
foritech --help
foritech keygen --out mykey.bin
foritech encrypt --in secret.txt --out secret.txt.enc
foritech decrypt --in secret.txt.enc --out secret.txt
```

See `docs/CLI_WRAPPER_SYNC.md` for how this wrapper stays in sync with the native CLI.
```

---

## 6) examples (shell)

### examples/01_keygen.sh
```bash
#!/usr/bin/env bash
set -euo pipefail
foritech keygen --out mykey.bin
```

### examples/02_encrypt_file.sh
```bash
#!/usr/bin/env bash
set -euo pipefail
: "${INPUT:=secret.txt}"
: "${OUTPUT:=secret.txt.enc}"
foritech encrypt --in "$INPUT" --out "$OUTPUT"
```

### examples/03_decrypt_file.sh
```bash
#!/usr/bin/env bash
set -euo pipefail
: "${INPUT:=secret.txt.enc}"
: "${OUTPUT:=secret.txt}"
foritech decrypt --in "$INPUT" --out "$OUTPUT"
```

> Make scripts executable: `chmod +x examples/*.sh`

---

## 7) sdk/tests/test_cli_wrapper_smoke.py

```python
import os
import shutil
import subprocess
import sys
import pytest

pytestmark = pytest.mark.skipif(shutil.which("docker") is None, reason="docker not available")


def test_foritech_help():
    proc = subprocess.run([sys.executable, "-m", "foritech_cli.main", "--help"], capture_output=True, text=True)
    assert proc.returncode == 0
    assert "Foritech CLI" in proc.stdout


def test_foritech_image_override_env(monkeypatch):
    monkeypatch.setenv("FORITECH_IMAGE", "alpine:3.19")
    # We don't actually run a command here to avoid needing the inner CLI
    proc = subprocess.run([sys.executable, "-m", "foritech_cli.main", "--help"], capture_output=True, text=True)
    assert proc.returncode == 0
```

> This is a lightweight smoke test to ensure the module loads and help works. E2E invoking the container is optional here and better suited for a separate job.

---

## 8) .github/workflows/cli-wrapper-smoke.yml

```yaml
name: CLI Wrapper Smoke

on:
  push:
    branches: [ main ]
  pull_request:

jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install sdk (editable)
        run: |
          cd sdk
          pip install -U pip
          pip install -e .

      - name: foritech --help should work
        run: |
          foritech --help
```

> This verifies the wrapper installs and prints help on Ubuntu with Docker available in the runner environment.

---

## 9) Commit checklist

```bash
git add sdk/src/foritech_cli docs/CLI_WRAPPER_SYNC.md examples/ \
        sdk/tests/test_cli_wrapper_smoke.py .github/workflows/cli-wrapper-smoke.yml
# Also update sdk/pyproject.toml and README.md

git add sdk/pyproject.toml README.md

git commit -m "feat(cli): add Docker-based wrapper (Variant A) with smoke tests and docs"

git push -u origin <your-branch>
```

---

## 10) Notes
- Replace `YOUR_PINNED_DIGEST_HERE` with the actual image digest you publish.
- Update `inner_cmd` to match the command exposed inside your container (`foritech-cli` is a placeholder).
- Keep verb names identical to what Variant B will implement to ease transition.


# Foritech SDK

Лек Python SDK за криптография и интеграция с Foritech Secure System.

## Инсталация
```bash
pip install foritech-sdk

```

##Quickstart

```bash
from foritech import __version__
print("foritech-sdk:", __version__)
```
-(Пример) Шифриране на байтове с Data Encryption Key (DEK)

-Примерният API е минимален и стабилен; ако сменим имена – ще обновим README.

```bash

from foritech import errors

def encrypt_bytes(data: bytes, key: bytes) -> bytes:
    # TODO: използвай реалния SDK API при готовност
    if not key:
        raise errors.EncryptError("Missing key")
    return data[::-1]  # demo only

def decrypt_bytes(ct: bytes, key: bytes) -> bytes:
    if not key:
        raise errors.DecryptError("Missing key")
    return ct[::-1]

pt = b"hello"
key = b"\x00" * 32
ct = encrypt_bytes(pt, key)
rt = decrypt_bytes(ct, key)
assert rt == pt

```
----

##Полезни връзки

--Репо: https://github.com/foritech-secure-system/foritech-secure-system

--Issues: https://github.com/foritech-secure-system/foritech-secure-system/issues

##Лиценз



---


