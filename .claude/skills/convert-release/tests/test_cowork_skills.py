import contextlib
import io
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "setup"))
import cowork_skills as cs  # noqa: E402


def skill(root, name, front=None, files=None):
    d = root / ".claude" / "skills" / name
    d.mkdir(parents=True)
    front = front if front is not None else f"name: {name}\ndescription: Does {name} things."
    (d / "SKILL.md").write_text(f"---\n{front}\n---\nbody\n", encoding="utf-8")
    for rel, text in (files or {}).items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_text(text, encoding="utf-8")
    return d


def run(*args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        code = cs.main([str(a) for a in args])
    return code, buf.getvalue()


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.td = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.td, True)

    def test_valid_skill_passes(self):
        self.assertEqual(cs.check(skill(self.td, "good")), [])

    def test_folded_description_with_angle_bracket_fails(self):
        d = skill(self.td, "bad", "name: bad\ndescription: >\n  Use for `<tag>` work.")
        self.assertIn("description contains < or >", cs.check(d))

    def test_claude_code_only_keys_fail(self):
        d = skill(self.td, "teach", "name: teach\ndescription: Teach.\nargument-hint: \"x\"")
        self.assertTrue(any("not allowed" in p for p in cs.check(d)))

    def test_yaml_breaking_forms_fail(self):
        d = skill(self.td, "colon", "name: colon\ndescription: Use when: the owner asks.")
        self.assertTrue(any("unquoted ': '" in p for p in cs.check(d)))
        d = skill(self.td, "nospace", "name: nospace\ndescription:Does things.")
        self.assertTrue(any("space after the colon" in p for p in cs.check(d)))
        d = skill(self.td, "quoted", "name: quoted\ndescription: \"Use when: the owner asks.\"")
        self.assertEqual(cs.check(d), [])

    def test_nested_skill_md_fails(self):
        d = skill(self.td, "nest", files={"sub/SKILL.md": "x"})
        self.assertTrue(any("extra SKILL.md" in p for p in cs.check(d)))


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.td = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.td, True)
        self.ws = self.td / "ws"
        skill(self.ws, "personal-memory", files={"gate.py": "x", "__pycache__/gate.pyc": "x"})
        skill(self.ws, "hyperframes")
        skill(self.ws, "convert-release")

    def test_core_only_with_folder_at_zip_root(self):
        code, log = run("package", self.td / "out", "--workspace", self.ws)
        self.assertEqual(code, 0, log)
        self.assertEqual(sorted(p.name for p in (self.td / "out").iterdir()), ["personal-memory.skill"])
        names = zipfile.ZipFile(self.td / "out" / "personal-memory.skill").namelist()
        self.assertEqual(sorted(names), ["personal-memory/SKILL.md", "personal-memory/gate.py"])

    def test_video_adds_other_skills_but_never_convert_release(self):
        run("package", self.td / "out", "--workspace", self.ws, "--video")
        self.assertEqual(sorted(p.name for p in (self.td / "out").iterdir()),
                         ["hyperframes.skill", "personal-memory.skill"])

    def test_update_packages_only_new_or_changed_and_lists_removed(self):
        skill(self.ws, "teach")
        skill(self.ws, "adhd")
        run("package", self.td / "first", "--workspace", self.ws)
        old = self.td / "old"
        shutil.copytree(self.ws, old)
        new = self.ws
        shutil.rmtree(new / ".claude/skills/teach")
        (new / ".claude/skills/personal-memory/gate.py").write_text("changed", encoding="utf-8")
        skill(new, "meeting")
        code, log = run("package", self.td / "out", "--workspace", new, "--previous", old)
        self.assertEqual(code, 0, log)
        self.assertIn("removed: teach", log)
        self.assertEqual(sorted(p.name for p in (self.td / "out").iterdir()),
                         ["meeting.skill", "personal-memory.skill"])

    def test_update_keeps_video_choice_and_catches_skills_not_packaged_before(self):
        run("package", self.td / "first", "--workspace", self.ws, "--video")
        old = self.td / "old"
        shutil.copytree(self.ws, old)
        skill(self.ws, "general-video")
        code, log = run("package", self.td / "out", "--workspace", self.ws, "--previous", old)
        self.assertEqual(code, 0, log)
        self.assertEqual([p.name for p in (self.td / "out").iterdir()], ["general-video.skill"])

    def test_update_from_loader_setup_packages_everything(self):
        old = self.td / "old"
        shutil.copytree(self.ws, old)
        code, log = run("package", self.td / "out", "--workspace", self.ws, "--previous", old)
        self.assertEqual(code, 0, log)
        self.assertIn("loaders: yes", log)
        self.assertEqual([p.name for p in (self.td / "out").iterdir()], ["personal-memory.skill"])

    def test_previous_must_not_be_this_workspace(self):
        code, log = run("package", self.td / "out", "--workspace", self.ws, "--previous", self.ws)
        self.assertEqual(code, 2)
        self.assertIn("old workspace folder", log)

    def test_invalid_skill_is_reported_and_exit_1(self):
        skill(self.ws, "youtube", "name: youtube\ndescription: Use `/youtube <url>`.")
        code, log = run("package", self.td / "out", "--workspace", self.ws)
        self.assertEqual(code, 1)
        self.assertIn("FAILED youtube", log)


if __name__ == "__main__":
    unittest.main()
