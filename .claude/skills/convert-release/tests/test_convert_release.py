import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import convert_release as cr  # noqa: E402


def release(root, files):
    """Write an upstream Release: files maps path -> text; all are listed in MANIFEST.json."""
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text.encode("utf-8"))
    man = {"release": 9, "files": {rel: {"class": "merge", "sha256": "x", "mode": "644"} for rel in files}}
    (root / "MANIFEST.json").write_text(json.dumps(man), encoding="utf-8")


def workspace(root):
    root.mkdir()
    (root / "CLAUDE.md").write_text("ws", encoding="utf-8")
    for rel in [*cr.KEEP_WORKSPACE, *cr.WORKSPACE_ONLY]:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"workspace {rel}", encoding="utf-8")
    return root


def run(*args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        code = cr.main([str(a) for a in args])
    return code, buf.getvalue()


class ConvertTextTests(unittest.TestCase):
    def test_paths_and_escaped_name_are_renamed(self):
        out = cr.convert_text("x.py", "see .agents/skills/a and AGENTS.md; re AGENTS\\.md")
        self.assertEqual(out, "see .claude/skills/a and CLAUDE.md; re CLAUDE\\.md")

    def test_agents_md_kept_in_agents_library(self):
        rel = ".claude/skills/workflow-builder/agents-library/x.md"
        self.assertIn("AGENTS.md", cr.convert_text(rel, "AGENTS.md standard"))

    def test_crlf_round_trips(self):
        self.assertEqual(cr.convert_text("x.md", "a\r\nb .agents/\r\n"), "a\r\nb .claude/\r\n")
        self.assertEqual(cr.convert_text("x.md", "a\nb\n"), "a\nb\n")

    def test_rule_that_no_longer_matches_stops(self):
        with self.assertRaises(SystemExit) as cm:
            cr.convert_text("memory/rules.md", "| Always | | | |\n")
        self.assertIn("rule no longer matches", str(cm.exception))

    def test_decisions_index_keeps_other_entries_and_drops_empty_sections(self):
        text = ("# Decision Index\n\nGenerated.\n\n## projects\n\n"
                "- [Starter-agent GitHub repository](a.md) x\n- [Keep me](b.md) y\n\n"
                "## workstation\n\n- [Codex workspace with hooks skipped](c.md) z\n")
        out = cr.convert_text("memory/decisions/index.md", text)
        self.assertEqual(out, "# Decision Index\n\nGenerated.\n\n## projects\n\n- [Keep me](b.md) y\n")


class MainTests(unittest.TestCase):
    def setUp(self):
        self.td = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(self.td, ignore_errors=True))
        self.src, self.out = self.td / "rel", self.td / "out"
        self.ws = workspace(self.td / "ws")

    def test_converts_drops_and_keeps(self):
        files = {".agents/skills/a/SKILL.md": "Use .agents/skills/a\n",
                 ".agents/skills/a/agents/openai.yaml": "x",
                 ".agents/skills/adhd/SKILL.md": "codex version"}
        release(self.src, files)
        (self.src / "memory/decisions/projects").mkdir(parents=True)
        (self.src / "memory/decisions/projects/decision-github-repository.md").write_text("x")
        code, log = run(self.src, self.out, self.ws)
        self.assertEqual(code, 0, log)
        self.assertEqual((self.out / ".claude/skills/a/SKILL.md").read_text(), "Use .claude/skills/a\n")
        self.assertFalse((self.out / ".claude/skills/a/agents/openai.yaml").exists())
        self.assertFalse((self.out / "memory/decisions").exists())
        self.assertEqual((self.out / ".claude/skills/adhd/SKILL.md").read_text(),
                         "workspace .claude/skills/adhd/SKILL.md")
        self.assertIn("upstream changed .agents/skills/adhd/SKILL.md", log)
        man = json.loads((self.out / "MANIFEST.json").read_text())
        self.assertEqual(sorted(man["files"]), sorted([".claude/skills/a/SKILL.md", ".claude/skills/adhd/SKILL.md",
                                                       *cr.WORKSPACE_ONLY]))
        self.assertTrue((self.out / ".claude/setup/cowork_skills.py").is_file())
        self.assertNotIn("warning:", log)

    def test_unlisted_upstream_file_is_reported(self):
        release(self.src, {"a.md": "x"})
        (self.src / "stray.md").write_text("x")
        code, log = run(self.src, self.out, self.ws)
        self.assertEqual(code, 0, log)
        self.assertIn("warning: stray.md", log)

    def test_wrong_workspace_writes_nothing(self):
        release(self.src, {"a.md": "x"})
        code, log = run(self.src, self.out, self.src)
        self.assertEqual(code, 2)
        self.assertIn("is not this workspace", log)
        self.assertFalse(self.out.exists())

    def test_failed_rule_leaves_no_output(self):
        release(self.src, {"a.md": "x", "memory/rules.md": "no codex row\n"})
        with self.assertRaises(SystemExit):
            run(self.src, self.out, self.ws)
        self.assertFalse(self.out.exists())
        self.assertFalse(self.out.with_name("out.partial").exists())


if __name__ == "__main__":
    unittest.main()
