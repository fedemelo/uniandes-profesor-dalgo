from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from autograder.grader import languages


class LanguageStagingTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _write(self, name: str, content: str) -> Path:
        path = self.tmp / "source" / name
        path.parent.mkdir(exist_ok=True)
        path.write_text(content)
        return path

    def test_python_stage(self):
        source = self._write("weird_name.py", "print('hi')\n")
        workdir = self.tmp / "work"
        workdir.mkdir()

        staged = languages.Python().stage(source, workdir)

        self.assertIsNone(staged.compile_cmd)
        self.assertEqual(staged.run_cmd, ["python3", "main.py"])
        self.assertEqual((workdir / "main.py").read_text(), "print('hi')\n")

    def test_c_stage(self):
        source = self._write("sol.c", "int main() { return 0; }\n")
        workdir = self.tmp / "work"
        workdir.mkdir()

        staged = languages.C().stage(source, workdir)

        self.assertEqual(staged.compile_cmd, ["gcc", "-O2", "-o", "main", "main.c"])
        self.assertEqual(staged.run_cmd, ["./main"])
        self.assertTrue((workdir / "main.c").is_file())

    def test_java_stage_uses_public_class_name(self):
        source = self._write(
            "anything.java",
            "import java.util.*;\npublic class Solution {\n  public static void main(String[] a) {}\n}\n",
        )
        workdir = self.tmp / "work"
        workdir.mkdir()

        staged = languages.Java().stage(source, workdir)

        self.assertTrue((workdir / "Solution.java").is_file())
        self.assertEqual(staged.compile_cmd, ["javac", "Solution.java"])
        self.assertEqual(staged.run_cmd, ["java", "Solution"])

    def test_java_stage_prefers_public_class_over_a_helper_class_declared_first(self):
        source = self._write(
            "anything.java",
            "class Node {\n  int val;\n}\n\npublic class Main {\n  public static void main(String[] a) {}\n}\n",
        )
        workdir = self.tmp / "work"
        workdir.mkdir()

        staged = languages.Java().stage(source, workdir)

        self.assertTrue((workdir / "Main.java").is_file())
        self.assertEqual(staged.compile_cmd, ["javac", "Main.java"])
        self.assertEqual(staged.run_cmd, ["java", "Main"])

    def test_java_stage_prefers_public_final_class_over_a_helper_class_declared_first(self):
        source = self._write(
            "anything.java",
            "class Node {\n  int val;\n}\n\npublic final class Main {\n  public static void main(String[] a) {}\n}\n",
        )
        workdir = self.tmp / "work"
        workdir.mkdir()

        staged = languages.Java().stage(source, workdir)

        self.assertTrue((workdir / "Main.java").is_file())
        self.assertEqual(staged.compile_cmd, ["javac", "Main.java"])
        self.assertEqual(staged.run_cmd, ["java", "Main"])

    def test_java_stage_falls_back_when_no_class_found(self):
        source = self._write("weird.java", "// not really java\n")
        workdir = self.tmp / "work"
        workdir.mkdir()

        staged = languages.Java().stage(source, workdir)

        self.assertTrue((workdir / "Main.java").is_file())
        self.assertEqual(staged.run_cmd, ["java", "Main"])

    def test_detect_dispatches_by_extension(self):
        self.assertIsInstance(languages.detect(Path("sol.py")), languages.Python)
        self.assertIsInstance(languages.detect(Path("Sol.java")), languages.Java)
        self.assertIsInstance(languages.detect(Path("sol.c")), languages.C)
        self.assertIsNone(languages.detect(Path("notes.tex")))


if __name__ == "__main__":
    unittest.main()
