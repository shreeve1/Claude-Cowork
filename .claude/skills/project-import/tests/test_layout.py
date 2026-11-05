import re
import sys
import tempfile
import unittest
import zipfile
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
        self.assertEqual(fields["name"].strip(), "project-import")
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

    def test_open_load_scopes_task_rows(self):
        open_section = self.section("Open a project")
        for needle in ("whose task this README links", "inside this project's folder"):
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

    def import_text(self):
        return self.read_required("import.md")

    def test_single_source_line_format(self):
        text = self.import_text()
        source_formats = re.findall(r"Source: Claude Project[^\n`]*", text)
        self.assertEqual(
            source_formats,
            ["Source: Claude Project <id>, imported YYYY-MM-DD"],
        )
        self.assertNotIn("naming the project's name instead of an ID", text)

    def test_reads_cowork_project_copy(self):
        text = self.import_text()
        for needle in ("metadata.json", "memory.md", "docs/", "files/", "Add folder"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_four_verdicts(self):
        text = self.import_text()
        for verdict in ("`project`", "`owner-wide`", "`covered`", "`drop`"):
            with self.subTest(verdict=verdict):
                self.assertIn(verdict, text)

    def test_approval_before_write(self):
        text = self.import_text()
        self.assertIn("Write nothing until", text)
        write_step = re.search(r"^\d+\. \*\*Write", text, re.M)
        if write_step is None:
            self.fail("Missing numbered Write step")
        self.assertLess(text.index("Write nothing until"), write_step.start())

    def test_reimport_never_overwrites(self):
        text = self.import_text()
        for needle in ("Source:", "differences", "not deleted"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_files_limits_named(self):
        text = self.import_text()
        for needle in ("Word", "text only", "ID", "no saved history"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_credentials_by_line(self):
        text = self.import_text()
        self.assertRegex(text, r"(?s)Screen every text source \(instructions, `memory.md`, `docs/`\).{0,120}by file and line, never any part of the value")
        self.assertIn("kept with that line removed", text)
        self.assertIn("which file and line held a credential, never any part of the value", text)
        self.assertNotIn("git-ignored", text)

    def test_no_copy_visible_fallback(self):
        text = self.import_text()
        for needle in ("paste", "Add project context from", "Add folder", "project page"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_project_copy_and_matching(self):
        text = self.import_text()
        for needle in (
            "project cache",
            "confirm the name before sorting",
            "ask the owner to name them",
            "glossary row or README title",
            "a pasted import used it as its id",
            "Never copy what a project file already says",
            "uses a Claude app tool",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_open_new_project_and_search_scope(self):
        text = self.read_required("SKILL.md")
        open_section = self.section("Open a project")
        for needle in ("Import or starting a new one", "Project README template", "<client_folder>/*/projects/"):
            with self.subTest(needle=needle):
                self.assertIn(needle, open_section)
        self.assertIn("skill/           # project skill source, if any", text)

    def test_batch(self):
        text = self.import_text()
        self.assertIn("one project per chat", text)
        self.assertRegex(text, r"(?s)done.{0,200}Source:|Source:.{0,200}done")

    def test_ends_with_open_as_proof(self):
        steps = re.findall(r"^\d+\. .*(?:\n(?!\d+\. ).+)*", self.import_text(), re.M)
        self.assertGreaterEqual(len(steps), 8)
        self.assertIn("Open a project", steps[-1])
        self.assertIn("briefing", steps[-1])

    def project_skills_text(self):
        return self.read_required("project-skills.md")

    def test_template_passes_cowork_checks(self):
        text = self.project_skills_text()
        blocks = re.findall(r"```markdown\n(.*?)\n```", text, re.S)
        self.assertEqual(len(blocks), 1, "Expected one fenced markdown template")
        template = blocks[0]
        for placeholder in ("<skill-name>", "<description>"):
            self.assertIn(placeholder, template)
        for needle in ("Open the project first", "## Steps"):
            self.assertIn(needle, template)
        filled = template.replace("<skill-name>", "brand-guide").replace(
            "<description>", "Apply the brand guide to new material. Use when drafting or reviewing branded content."
        )
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "brand-guide"
            folder.mkdir()
            (folder / "SKILL.md").write_text(filled, encoding="utf-8")
            self.assertEqual(cowork_skills.check(folder), [])
            dest = Path(tmp) / "brand-guide.skill"
            cowork_skills.package(folder, dest)
            with zipfile.ZipFile(dest) as archive:
                self.assertEqual(archive.namelist(), ["brand-guide/SKILL.md"])

    def test_steps_only_no_facts(self):
        text = self.project_skills_text()
        for needle in ("steps", "no facts", "README.md", "repeatable"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_requires_owner_approval_and_save_skill(self):
        text = self.project_skills_text()
        for needle in ("approval", "present_files", "Save skill", "skill/SKILL.md", "Skill: <name>"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_blocked_install_reported(self):
        text = self.project_skills_text()
        self.assertIn("forbids", text)
        self.assertIn("blocked", text)
        self.assertIn("opener", text)

    def test_name_collision_checked(self):
        text = self.project_skills_text()
        self.assertIn("installed", text)
        self.assertIn("shipped", text)
        self.assertIn(".claude/cowork/skills/index.json", text)

    def test_upload_rules_listed(self):
        text = self.project_skills_text()
        for needle in ("allowed-tools", "compatibility", "1024", "kebab-case", "64", "zipfile"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

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
