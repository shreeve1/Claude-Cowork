import re
import shutil
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
SKILLS = Path(__file__).resolve().parents[2]


class LayoutTests(unittest.TestCase):
    def read_required(self, name):
        path = SKILL / name
        self.assertTrue(path.is_file(), f"Missing {name}")
        return path.read_text(encoding="utf-8")

    def source_files(self):
        return sorted(path for path in SKILL.rglob("*") if path.suffix in {".md", ".py"})

    def test_frontmatter(self):
        text = self.read_required("SKILL.md")
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(match, "Missing frontmatter")
        fields = dict(line.split(":", 1) for line in match[1].splitlines())
        self.assertEqual(fields["name"].strip(), "memory-setup")
        description = fields["description"].lower()
        self.assertIn("set up memory", description)
        self.assertIn("migrate", description)
        self.assertNotIn("remember this", description)

    def test_every_reference_linked(self):
        text = self.read_required("SKILL.md")
        expected = {
            "where-things-go.md",
            "tracking-model.md",
            "sorting.md",
            "subagent-brief.md",
            "code-repos.md",
        }
        self.assertEqual({path.name for path in SKILL.glob("*.md")} - {"SKILL.md"}, expected)
        for path in SKILL.glob("*.md"):
            if path.name != "SKILL.md":
                with self.subTest(reference=path.name):
                    self.assertIn(path.name, text)

    def test_personal_memory_paths_exist(self):
        for path in self.source_files():
            matches = re.findall(
                r"(?:<skills>/)?personal-memory/[\w./-]+",
                path.read_text(encoding="utf-8"),
            )
            for match in matches:
                relative = match.removeprefix("<skills>/").rstrip(".,)/")
                with self.subTest(file=path.name, target=relative):
                    self.assertTrue((SKILLS / relative).exists(), relative)

    def test_personal_memory_copy_includes_task_formats(self):
        source = SKILLS / "personal-memory"
        with tempfile.TemporaryDirectory() as td:
            copied = Path(td) / "personal-memory"
            shutil.copytree(source, copied, ignore=shutil.ignore_patterns("tests", "__pycache__"))
            self.assertFalse((copied / "tests").exists())
            for name in ("SKILL.md", "tasks.md", "task-templates.md", "supporting-templates.md"):
                self.assertTrue((copied / name).is_file(), name)
            for path in copied.glob("*.md"):
                text = re.sub(r"^```.*?^```", "", path.read_text(encoding="utf-8"), flags=re.M | re.S)
                for target in re.findall(r"\]\(([^)]+\.md)\)", text):
                    if "/" not in target:
                        self.assertTrue((copied / target).is_file(), target)

    def test_sorting_verdicts(self):
        text = self.read_required("sorting.md")
        for verdict in (
            "covered",
            "stale",
            "history",
            "meta",
            "backlog",
            "keep",
            "client",
            "glossary",
        ):
            with self.subTest(verdict=verdict):
                self.assertRegex(text, rf"\b{verdict}\b")

    def test_no_personal_content(self):
        # Split fixtures so scanning this test does not flag the fixtures themselves.
        forbidden = (
            "ja" + "mes",
            "ita" + "stack",
            "ita" + "n8n",
            "home" + "lab",
            "Na" + "than",
        )
        for path in self.source_files():
            text = path.read_text(encoding="utf-8").lower()
            for word in forbidden:
                with self.subTest(file=str(path.relative_to(SKILL)), word=word):
                    self.assertNotIn(word.lower(), text)


if __name__ == "__main__":
    unittest.main()
