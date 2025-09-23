from __future__ import annotations
import argparse, os, shutil, subprocess, sys
from typing import List

DEFAULT_IMAGE = os.environ.get(
    "FORITECH_IMAGE",
    "docker.io/foritech/cli@sha256:5357e8eac9b2cd6d7b9b164cf8baa5a49fd6b9857cc8ba967bc8a2604231e616",
)

# If the container exposes a CLI binary, set FORITECH_INNER to its name (e.g., "foritech").
# If the container ENTRYPOINT is already the CLI, leave it empty to pass only subcommands.
DEFAULT_INNER = os.environ.get("FORITECH_INNER", "").strip()

def _docker_base_args() -> List[str]:
    args = ["docker","run","--rm","-i"]
    cwd = os.getcwd()
    args += ["-v", f"{cwd}:/work"]
    if os.name == "posix":
        try: args += ["-u", f"{os.getuid()}:{os.getgid()}"]
        except AttributeError: pass
    args += ["-w","/work"]
    for env_name in ("TZ","FORITECH_LOGLEVEL"):
        if env_name in os.environ:
            args += ["-e", f"{env_name}={os.environ[env_name]}"]
    return args

def _ensure_docker_available() -> None:
    if not shutil.which("docker"):
        print("Error: Docker is not installed or not in PATH.", file=sys.stderr)
        sys.exit(127)

def run_container(image: str, inner_args: List[str]) -> int:
    cmd = _docker_base_args() + [image] + inner_args
    try: return subprocess.run(cmd, check=False).returncode
    except KeyboardInterrupt: return 130
    except Exception as e:
        print(f"Runtime error: {e}", file=sys.stderr); return 2

def _prefixed(args: List[str]) -> List[str]:
    if DEFAULT_INNER:
        return [DEFAULT_INNER] + args
    return args  # rely on container ENTRYPOINT

def main(argv: List[str] | None = None) -> int:
    _ensure_docker_available()
    p = argparse.ArgumentParser(
        prog="foritech",
        description="Foritech CLI (Docker wrapper). Set FORITECH_IMAGE and FORITECH_INNER if needed.",
    )
    p.add_argument("--image", default=DEFAULT_IMAGE, help="Docker image (pinned digest or tag).")
    sub = p.add_subparsers(dest="command", required=True)

    # 1:1 подкоманди към вътрешния CLI
    p_help = sub.add_parser("help", help="Show inner CLI help or command-specific help.")
    p_help.add_argument("topic", nargs="*", help="Optional command to show help for")

    p_selftest = sub.add_parser("selftest", help="Run inner self tests.")
    p_meta = sub.add_parser("meta", help="Show metadata about the CLI/image.")

    # wrap/unwrap (1:1)
    p_wrap = sub.add_parser("wrap", help="Wrap/encrypt a file (maps to inner 'wrap').")
    p_wrap.add_argument("--in", dest="in_path", required=True)
    p_wrap.add_argument("--out", dest="out_path", required=True)
    p_wrap.add_argument("--aad", dest="aad", default=None)

    p_unwrap = sub.add_parser("unwrap", help="Unwrap/decrypt a file (maps to inner 'unwrap').")
    p_unwrap.add_argument("--in", dest="in_path", required=True)
    p_unwrap.add_argument("--out", dest="out_path", required=True)
    p_unwrap.add_argument("--aad", dest="aad", default=None)

    # Алиаси за удобство
    p_encrypt = sub.add_parser("encrypt", help="Alias for 'wrap'.")
    p_encrypt.add_argument("--in", dest="in_path", required=True)
    p_encrypt.add_argument("--out", dest="out_path", required=True)
    p_encrypt.add_argument("--aad", dest="aad", default=None)

    p_decrypt = sub.add_parser("decrypt", help="Alias for 'unwrap'.")
    p_decrypt.add_argument("--in", dest="in_path", required=True)
    p_decrypt.add_argument("--out", dest="out_path", required=True)
    p_decrypt.add_argument("--aad", dest="aad", default=None)

    # raw: директно подай аргументите към контейнера (без префикс)
    p_raw = sub.add_parser("raw", help="Pass args directly to container (no inner prefix).")
    p_raw.add_argument("args", nargs=argparse.REMAINDER)

    args = p.parse_args(argv)

    if args.command == "help":
        inner = ["help"] + args.topic
        return run_container(args.image, _prefixed(inner))

    if args.command == "selftest":
        return run_container(args.image, _prefixed(["selftest"]))

    if args.command == "meta":
        return run_container(args.image, _prefixed(["meta"]))

    if args.command in {"wrap", "encrypt"}:
        inner = ["wrap", "--in", args.in_path, "--out", args.out_path]
        if args.aad: inner += ["--aad", args.aad]
        return run_container(args.image, _prefixed(inner))

    if args.command in {"unwrap", "decrypt"}:
        inner = ["unwrap", "--in", args.in_path, "--out", args.out_path]
        if args.aad: inner += ["--aad", args.aad]
        return run_container(args.image, _prefixed(inner))

    if args.command == "raw":
        return run_container(args.image, args.args)

    p.print_usage(sys.stderr); return 1

if __name__ == "__main__":
    raise SystemExit(main())
