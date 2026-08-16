from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from autograder.grader import safe_zip


def _make_zip(path: Path, members: dict[str, bytes], compress: bool = True) -> None:
    compression = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
    with zipfile.ZipFile(path, "w", compression) as zf:
        for name, data in members.items():
            zf.writestr(name, data)


class SafeExtractAllTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_extracts_a_normal_zip(self):
        zip_path = self.tmp / "normal.zip"
        _make_zip(zip_path, {"a.txt": b"hello", "sub/b.txt": b"world"})

        target = self.tmp / "out"
        safe_zip.safe_extractall(zip_path, target)

        self.assertEqual((target / "a.txt").read_bytes(), b"hello")
        self.assertEqual((target / "sub" / "b.txt").read_bytes(), b"world")

    def test_rejects_path_traversal(self):
        zip_path = self.tmp / "evil.zip"
        _make_zip(zip_path, {"../escape.txt": b"pwned"})

        with self.assertRaises(safe_zip.UnsafeZipError):
            safe_zip.safe_extractall(zip_path, self.tmp / "out")

    def test_rejects_absolute_path(self):
        zip_path = self.tmp / "evil.zip"
        _make_zip(zip_path, {"/etc/passwd": b"pwned"})

        with self.assertRaises(safe_zip.UnsafeZipError):
            safe_zip.safe_extractall(zip_path, self.tmp / "out")

    def test_rejects_high_compression_ratio(self):
        zip_path = self.tmp / "bomb.zip"
        # Highly compressible payload: real zip bombs rely on exactly this.
        _make_zip(zip_path, {"bomb.bin": b"\0" * 50_000_000})

        with self.assertRaises(safe_zip.UnsafeZipError):
            safe_zip.safe_extractall(zip_path, self.tmp / "out")

    def test_rejects_over_byte_cap_even_with_honest_metadata(self):
        zip_path = self.tmp / "large.zip"
        # Incompressible-ish content so the ratio check alone wouldn't catch it;
        # the streamed byte cap should catch it regardless of what the header claims.
        import os

        _make_zip(zip_path, {"large.bin": os.urandom(200_000)}, compress=False)

        original_cap = safe_zip.MAX_UNCOMPRESSED_BYTES
        safe_zip.MAX_UNCOMPRESSED_BYTES = 100_000
        try:
            with self.assertRaises(safe_zip.UnsafeZipError):
                safe_zip.safe_extractall(zip_path, self.tmp / "out")
        finally:
            safe_zip.MAX_UNCOMPRESSED_BYTES = original_cap

    def test_rejects_too_many_members(self):
        zip_path = self.tmp / "many.zip"
        _make_zip(zip_path, {f"f{i}.txt": b"x" for i in range(10)})

        original_max = safe_zip.MAX_MEMBERS
        safe_zip.MAX_MEMBERS = 5
        try:
            with self.assertRaises(safe_zip.UnsafeZipError):
                safe_zip.safe_extractall(zip_path, self.tmp / "out")
        finally:
            safe_zip.MAX_MEMBERS = original_max


if __name__ == "__main__":
    unittest.main()
