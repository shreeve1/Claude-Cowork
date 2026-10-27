import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "cowork"))
import cowork_skills as cs  # noqa: E402


def skill(root, name, front=None, files=None):
    d = root / ".claude" / "skills" / name
    d.mkdir(parents=True, exist_ok=True)
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


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.td = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.td, True)
        self.ws = self.td / "ws"
        skill(self.ws, "personal-memory", files={"gate.py": "#!/usr/bin/env python3\n", "__pycache__/g.pyc": "x"})
        skill(self.ws, "hyperframes")
        skill(self.ws, "convert-release")
        self.pk = self.ws / cs.PACKAGES

    def test_build_sorts_core_and_video_and_skips_maintainer_skill(self):
        code, log = run("build", "--workspace", self.ws)
        self.assertEqual(code, 0, log)
        self.assertEqual(sorted(p.relative_to(self.pk).as_posix() for p in self.pk.glob("*/*.skill")),
                         ["core/personal-memory.skill", "video/hyperframes.skill"])
        z = zipfile.ZipFile(self.pk / "core/personal-memory.skill")
        self.assertEqual(sorted(z.namelist()), ["personal-memory/SKILL.md", "personal-memory/gate.py"])
        self.assertEqual(z.getinfo("personal-memory/gate.py").external_attr >> 16, 0o100755)
        index = json.loads((self.ws / cs.INDEX).read_text())
        self.assertEqual({n: e["set"] for n, e in index.items()}, {"personal-memory": "core", "hyperframes": "video"})

    def test_build_is_byte_identical_when_unchanged(self):
        run("build", "--workspace", self.ws)
        first = (self.pk / "core/personal-memory.skill").read_bytes()
        run("build", "--workspace", self.ws)
        self.assertEqual(first, (self.pk / "core/personal-memory.skill").read_bytes())

    def test_build_removes_stale_packages_and_reports_failures(self):
        run("build", "--workspace", self.ws)
        shutil.rmtree(self.ws / ".claude/skills/hyperframes")
        skill(self.ws, "youtube", "name: youtube\ndescription: Use `/youtube <url>`.")
        code, log = run("build", "--workspace", self.ws)
        self.assertEqual(code, 1)
        self.assertIn("FAILED youtube", log)
        self.assertFalse((self.pk / "video/hyperframes.skill").exists())


class ChangedTests(unittest.TestCase):
    def setUp(self):
        self.td = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.td, True)
        self.old, self.new = self.td / "old", self.td / "new"
        for n in ("personal-memory", "adhd", "teach", "hyperframes"):
            skill(self.old, n)
        run("build", "--workspace", self.old)
        shutil.copytree(self.old, self.new)

    def lines(self, *extra):
        run("build", "--workspace", self.new)
        code, log = run("changed", self.old, "--workspace", self.new, *extra)
        self.assertEqual(code, 0, log)
        return log.strip().splitlines()

    def test_unchanged_shows_nothing(self):
        self.assertEqual(self.lines(), ["nothing to install: no new or changed skills"])

    def test_new_changed_and_removed(self):
        (self.new / ".claude/skills/adhd/extra.md").write_text("x", encoding="utf-8")
        shutil.rmtree(self.new / ".claude/skills/teach")
        skill(self.new, "meeting")
        self.assertEqual(self.lines(), ["removed: teach", ".claude/cowork/skills/core/adhd.skill",
                                        ".claude/cowork/skills/core/meeting.skill"])

    def test_video_owner_gets_video_changes_core_owner_does_not(self):
        (self.new / ".claude/skills/hyperframes/x.md").write_text("x", encoding="utf-8")
        self.assertEqual(self.lines(), ["nothing to install: no new or changed skills"])
        self.assertEqual(self.lines("--video"), [".claude/cowork/skills/video/hyperframes.skill"])

    def test_loader_setup_gets_everything(self):
        shutil.rmtree(self.old / ".claude/cowork")
        out = self.lines()
        self.assertTrue(out[0].startswith("loaders: yes"))
        self.assertEqual(len(out), 4)

    def test_core_skill_moved_to_video_is_not_reported_removed(self):
        cs_core = cs.CORE
        self.addCleanup(setattr, cs, "CORE", cs_core)
        cs.CORE = tuple(n for n in cs_core if n != "adhd")
        self.assertEqual(self.lines(), ["moved to video: adhd", "nothing to install: no new or changed skills"])

    def test_earlier_package_edition_is_not_called_loaders(self):
        shutil.rmtree(self.old / ".claude/cowork")
        (self.old / ".claude/cowork-skills.json").write_text("{}", encoding="utf-8")
        out = self.lines()
        self.assertFalse(any(l.startswith("loaders") for l in out))
        self.assertEqual(len(out), 3)

    def test_old_workspace_must_differ(self):
        code, log = run("changed", self.new, "--workspace", self.new)
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
