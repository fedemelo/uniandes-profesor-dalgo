from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from autograder.grader import extract


def _make_export_zip(path: Path, folders: dict[str, dict[str, bytes]]) -> None:
    """Build a Brightspace-shaped export zip: folders keyed by name, each a dict of filename->bytes."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("index.html", b"<html>brightspace metadata</html>")
        for folder, files in folders.items():
            for filename, content in files.items():
                zf.writestr(f"{folder}/{filename}", content)


class LoadSubmissionsTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_parses_folder_name_and_finds_code_file(self):
        export = self.tmp / "export.zip"
        _make_export_zip(
            export,
            {
                "11111-465221 - Legit Student - 15 de agosto de 2026 1200": {
                    "sol.py": b"print(1)",
                    "writeup.pdf": b"%PDF-fake",
                },
            },
        )

        submissions = extract.load_submissions(export, self.tmp / "work")

        self.assertEqual(len(submissions), 1)
        submission = submissions[0]
        self.assertEqual(submission.student_id, "11111")
        self.assertEqual(submission.name, "Legit Student")
        self.assertEqual(submission.code_file.name, "sol.py")
        self.assertEqual(submission.notes, [])

    def test_ignores_pdf_and_picks_code_extension_only(self):
        export = self.tmp / "export.zip"
        _make_export_zip(
            export,
            {
                "22222-465221 - Someone - 15 de agosto de 2026 1000": {
                    "stray.tex": b"not code",
                    "sol.py": b"print(1)",
                },
            },
        )

        submissions = extract.load_submissions(export, self.tmp / "work")

        self.assertEqual(submissions[0].code_file.name, "sol.py")

    def test_keeps_latest_resubmission(self):
        export = self.tmp / "export.zip"
        _make_export_zip(
            export,
            {
                "33333-465221 - Resubmitter - 15 de agosto de 2026 1000": {"sol.py": b"print('old')"},
                "33333-465221 - Resubmitter - 15 de agosto de 2026 1800": {"sol.py": b"print('new')"},
            },
        )

        submissions = extract.load_submissions(export, self.tmp / "work")

        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0].code_file.read_bytes(), b"print('new')")

    def test_unzips_a_nested_student_archive(self):
        export = self.tmp / "export.zip"
        with zipfile.ZipFile(export, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("index.html", b"")
            nested = self.tmp / "nested.zip"
            with zipfile.ZipFile(nested, "w", zipfile.ZIP_DEFLATED) as nzf:
                nzf.writestr("sol.py", b"print('nested')")
            zf.write(nested, "44444-465221 - Zipper - 15 de agosto de 2026 1000/Tarea.zip")

        submissions = extract.load_submissions(export, self.tmp / "work")

        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0].code_file.read_bytes(), b"print('nested')")

    def test_bomb_in_one_students_zip_does_not_break_the_others(self):
        export = self.tmp / "export.zip"
        # ZIP_STORED for the outer archive: wrapping an already-compressed nested "bomb.zip" in
        # another DEFLATE layer can itself look like a high compression ratio, which would trip
        # the top-level check before we even get to the nested-archive rejection this test targets.
        with zipfile.ZipFile(export, "w", zipfile.ZIP_STORED) as zf:
            zf.writestr("index.html", b"")
            bomb = self.tmp / "bomb.zip"
            with zipfile.ZipFile(bomb, "w", zipfile.ZIP_DEFLATED) as bzf:
                bzf.writestr("bomb.bin", b"\0" * 50_000_000)
            zf.write(bomb, "55555-465221 - Bomb Student - 15 de agosto de 2026 1000/Tarea.zip")
            zf.writestr("66666-465221 - Legit Student - 15 de agosto de 2026 1000/sol.py", b"print(1)")

        submissions = extract.load_submissions(export, self.tmp / "work")

        by_id = {s.student_id: s for s in submissions}
        self.assertIsNone(by_id["55555"].code_file)
        self.assertTrue(by_id["55555"].notes)
        self.assertEqual(by_id["66666"].code_file.name, "sol.py")

    def test_ignores_non_matching_top_level_entries(self):
        export = self.tmp / "export.zip"
        _make_export_zip(export, {"77777-465221 - Fine - 15 de agosto de 2026 1000": {"sol.py": b"print(1)"}})

        submissions = extract.load_submissions(export, self.tmp / "work")

        # index.html shouldn't produce a phantom submission
        self.assertEqual(len(submissions), 1)


if __name__ == "__main__":
    unittest.main()
