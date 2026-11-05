import re
import sys
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
SKILLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILLS.parent / "cowork"))

import cowork_skills  # type: ignore  # noqa: E402


class LayoutTests(unittest.TestCase):
    def read_required(self, name):
        path = SKILL / name
        self.assertTrue(path.is_file(), f"Missing {name}")
        return path.read_text(encoding="utf-8")

    def source_files(self):
        return sorted(path for path in SKILL.rglob("*") if path.suffix in {".md", ".py"})

    def section(self, heading):
        text = self.read_required("SKILL.md")
        match = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.M | re.S)
        if match is None:
            self.fail(f"Missing section: {heading}")
        return match[1]

    def test_frontmatter(self):
        text = self.read_required("SKILL.md")
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
        if match is None:
            self.fail("Missing frontmatter")
        fields = dict(line.split(":", 1) for line in match[1].splitlines())
        self.assertEqual(fields["name"].strip(), "project")
        description = fields["description"].strip()
        self.assertTrue(description.startswith("Project"), "Front-load the word Project")
        for word in ("open", "import", "skill"):
            self.assertIn(word, description.lower())
        self.assertIn("Claude", description)
        self.assertEqual(cowork_skills.check(SKILL), [])

    def test_every_reference_linked(self):
        text = self.read_required("SKILL.md")
        expected = {"import.md", "project-skills.md"}
        self.assertEqual({path.name for path in SKILL.glob("*.md")} - {"SKILL.md"}, expected)
        for name in expected:
            with self.subTest(reference=name):
                self.assertIn(name, text)

    def test_sections_present(self):
        for heading in ("Find the home", "Open a project", "Import", "Project skills"):
            with self.subTest(heading=heading):
                self.section(heading)

    def test_home_from_schema(self):
        text = self.read_required("SKILL.md")
        for needle in ("memory/schema.json", "client_folder", "client_dirs", "memory/preferences/document-scaffolding.md"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)
        # Homes come from the schema, never from a fixed word.
        self.assertNotIn("clients/", text)

    def test_readme_line_formats(self):
        text = self.read_required("SKILL.md")
        self.assertIn("Source: Claude Project <id>, imported YYYY-MM-DD", text)
        self.assertIn("Skill: <name>", text)

    def test_open_loads_every_link(self):
        open_section = self.section("Open a project")
        for needle in ("README.md", "instructions.md", "tasks/index.md", "opened or reported missing"):
            with self.subTest(needle=needle):
                self.assertIn(needle, open_section)

    def test_open_asks_on_multiple_matches(self):
        open_section = self.section("Open a project")
        self.assertIn("several", open_section)
        self.assertIn("ask which", open_section)

    def test_instructions_scoped(self):
        text = self.read_required("SKILL.md")
        self.assertIn("safety rules win", text)
        self.assertIn("Switching projects", text)

    def test_brief_names_project_skill(self):
        open_section = self.section("Open a project")
        self.assertIn("Skill:", open_section)
        self.assertIn("name the skill in the briefing", open_section)

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

    def test_no_personal_content(self):
        # Split fixtures so scanning this test does not flag the fixtures themselves.
        forbidden = (
            "ja" + "mes",
            "open" + "ly",
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
