from __future__ import annotations

import hashlib
import json
import mimetypes
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import requests


@dataclass
class UploadResult:
    path: Path
    status_code: int
    response_text: str


def iter_files(directory: Path, recursive: bool = True) -> Iterator[Path]:
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    if recursive:
        for root, _, files in os.walk(directory):
            for name in files:
                yield Path(root) / name
    else:
        for entry in directory.iterdir():
            if entry.is_file():
                yield entry


def guess_mime(file_path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(file_path))
    return mime or "application/octet-stream"


def sha256sum(file_path: Path, chunk_size: int = 1024 * 1024) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


class FileUploader:
    def __init__(
        self,
        endpoint: str,
        token: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        timeout_seconds: int = 30,
        verify_tls: bool = True,
    ) -> None:
        self.endpoint = endpoint
        self.token = token
        self.session = requests.Session()
        self.timeout_seconds = timeout_seconds
        self.verify_tls = verify_tls
        self.extra_headers = extra_headers or {}

    def _headers(self, file_path: Path) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "Content-Type": guess_mime(file_path),
            "X-File-Path": str(file_path),
            "X-File-Sha256": sha256sum(file_path),
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        headers.update(self.extra_headers)
        return headers

    def upload_file(self, file_path: Path) -> UploadResult:
        file_path = Path(file_path)
        with open(file_path, "rb") as f:
            resp = self.session.post(
                self.endpoint,
                data=f,
                headers=self._headers(file_path),
                timeout=self.timeout_seconds,
                verify=self.verify_tls,
            )
        return UploadResult(path=file_path, status_code=resp.status_code, response_text=resp.text)

    def upload_directory(
        self,
        directory: Path,
        recursive: bool = True,
        include_hidden: bool = False,
        dry_run: bool = False,
    ) -> List[UploadResult]:
        results: List[UploadResult] = []
        for file_path in iter_files(Path(directory), recursive=recursive):
            if not include_hidden:
                parts = file_path.relative_to(Path(directory)).parts
                if any(part.startswith(".") for part in parts):
                    continue
            if dry_run:
                results.append(UploadResult(file_path, 0, "DRY_RUN"))
                continue
            results.append(self.upload_file(file_path))
        return results

