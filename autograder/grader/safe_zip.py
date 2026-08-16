from __future__ import annotations

import zipfile
from pathlib import Path

MAX_MEMBERS = 2000
MAX_UNCOMPRESSED_BYTES = 100 * 1024 * 1024  # 100 MB per zip
MAX_COMPRESSION_RATIO = 100  # cheap pre-check; the byte cap below is the real backstop
_CHUNK_SIZE = 1024 * 1024


class UnsafeZipError(Exception):
    pass


def _reject_unsafe_path(filename: str) -> None:
    parts = Path(filename).parts
    if Path(filename).is_absolute() or ".." in parts:
        raise UnsafeZipError(f"unsafe path in archive: {filename}")


def safe_extractall(zip_path: Path, target: Path) -> None:
    """Extract `zip_path` into `target`, bounding member count, path traversal, and total bytes.

    Bytes are counted from the actual decompressed stream (not the zip's own size metadata,
    which an attacker can misstate), so this holds even against a mislabeled zip bomb.
    """
    with zipfile.ZipFile(zip_path) as zf:
        infos = zf.infolist()
        if len(infos) > MAX_MEMBERS:
            raise UnsafeZipError(f"{zip_path.name}: {len(infos)} entries exceeds limit of {MAX_MEMBERS}")

        for info in infos:
            if info.compress_size > 0 and info.file_size / info.compress_size > MAX_COMPRESSION_RATIO:
                ratio = info.file_size / info.compress_size
                raise UnsafeZipError(
                    f"{zip_path.name}: {info.filename} claims a {ratio:.0f}x compression ratio, "
                    f"exceeds limit of {MAX_COMPRESSION_RATIO}x"
                )

        total_written = 0
        for info in infos:
            if info.is_dir():
                continue
            _reject_unsafe_path(info.filename)
            dest = target / info.filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, open(dest, "wb") as out:
                while chunk := src.read(_CHUNK_SIZE):
                    total_written += len(chunk)
                    if total_written > MAX_UNCOMPRESSED_BYTES:
                        raise UnsafeZipError(
                            f"{zip_path.name}: extraction exceeds "
                            f"{MAX_UNCOMPRESSED_BYTES // (1024 * 1024)} MB cap"
                        )
                    out.write(chunk)
