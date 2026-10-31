import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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

    def test_historical_evidence_preserves_original_paths_and_clients(self):
        text = "Native Codex NOT RUN; fixture .agents/skills/ and AGENTS.md.\r\n"
        self.assertEqual(cr.convert_text("docs/testing/workspace-tasks-cases.md", text), text)

    def test_crlf_round_trips(self):
        self.assertEqual(cr.convert_text("x.md", "a\r\nb .agents/\r\n"), "a\r\nb .claude/\r\n")
        self.assertEqual(cr.convert_text("x.md", "a\nb\n"), "a\nb\n")

    def test_rule_that_no_longer_matches_stops(self):
        with self.assertRaises(SystemExit) as cm:
            cr.convert_text("memory/rules.md", "| Always | | | |\n")
        self.assertIn("rule no longer matches", str(cm.exception))

    def test_saved_task_routing_keeps_cowork_environment(self):
        text = ("# Rules\n\n| When | Lead | Also load | Note |\n|---|---|---|---|\n"
                "| Always | | `tasks/index.md` | Optional; skip absence without creating files. |\n"
                "| Updating this workspace to a new Release | | "
                "`memory/decisions/workstation/decision-codex-workspace.md` | Re-apply Codex. |\n")
        out = cr.convert_text("memory/rules.md", text)
        self.assertIn("| Always | | `tasks/index.md` | Optional;", out)
        self.assertIn("| Always | | `memory/preferences/cowork-environment.md` | |", out)
        self.assertNotIn("decision-codex-workspace", out)

    def test_saved_task_description_has_no_unquoted_colon(self):
        text = ("---\nname: personal-memory\ndescription: Use for saved workspace tasks: "
                "create, look up, continue, review, complete or archive a task.\n---\n")
        out = cr.convert_text(".claude/skills/personal-memory/SKILL.md", text)
        self.assertIn("saved workspace tasks (create,", out)
        self.assertNotIn("tasks: create", out)
        self.assertIn("archive a task).", out)

    def test_decisions_index_keeps_other_entries_and_drops_empty_sections(self):
        text = ("# Decision Index\n\nGenerated.\n\n## projects\n\n"
                "- [Starter-agent GitHub repository](a.md) x\n- [Keep me](b.md) y\n\n"
                "## workstation\n\n- [Codex workspace with hooks skipped](c.md) z\n")
        out = cr.convert_text("memory/decisions/index.md", text)
        self.assertEqual(out, "# Decision Index\n\nGenerated.\n\n## projects\n\n- [Keep me](b.md) y\n")


class TreeShaTests(unittest.TestCase):
    def test_line_endings_do_not_change_the_hash(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td, "a"), Path(td, "b")
            for root, text in ((a, b"x\ny\n"), (b, b"x\r\ny\r\n")):
                (root / "d").mkdir(parents=True)
                (root / "d/f.md").write_bytes(text)
            self.assertEqual(cr.tree_sha(a, {"d/f.md"}), cr.tree_sha(b, {"d/f.md"}))


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
        self.assertTrue((self.out / ".claude/cowork/cowork_skills.py").is_file())
        self.assertNotIn("warning:", log)

    def test_unlisted_upstream_file_is_reported(self):
        release(self.src, {"a.md": "x"})
        (self.src / "stray.md").write_text("x")
        code, log = run(self.src, self.out, self.ws)
        self.assertEqual(code, 0, log)
        self.assertIn("warning: stray.md", log)

    def test_new_memory_files_and_empty_task_index_are_included(self):
        release(self.src, {"a.md": "x"})
        extras = {
            ".agents/skills/personal-memory/recovery.py": "backup only\n",
            ".agents/skills/personal-memory/procedures.py": "read only\n",
            ".agents/skills/personal-memory/tasks.md": "Use task-templates.md\n",
            ".agents/skills/personal-memory/task-templates.md": "# Task\n",
            ".agents/skills/personal-memory/supporting-templates.md": "# Proposal\n",
            ".agents/skills/personal-memory/tests/test_tasks_policy.py": "test\n",
            "tasks/index.md": "# Active tasks\n",
        }
        for rel, text in extras.items():
            path = self.src / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        code, log = run(self.src, self.out, self.ws)
        self.assertEqual(code, 0, log)
        self.assertNotIn("warning:", log)
        manifest = json.loads((self.out / "MANIFEST.json").read_text())["files"]
        for rel, text in extras.items():
            converted = cr.new_path(rel)
            self.assertEqual((self.out / converted).read_text(), text)
            self.assertEqual(manifest[converted]["class"], "seed" if rel == "tasks/index.md" else "merge")

    def test_recovery_and_runtime_state_are_never_copied_even_if_listed(self):
        excluded = {f"{folder}/private.md": "private" for folder in cr.DROP_DIRS}
        release(self.src, {"a.md": "x", **excluded})
        code, log = run(self.src, self.out, self.ws)
        self.assertEqual(code, 0, log)
        self.assertNotIn("warning:", log)
        manifest = json.loads((self.out / "MANIFEST.json").read_text())["files"]
        for rel in excluded:
            self.assertFalse((self.out / rel).exists())
            self.assertNotIn(rel, manifest)

    def test_kept_skill_drift_uses_source_bytes_not_stale_manifest(self):
        rel = ".agents/skills/adhd/SKILL.md"
        pinned = cr.KEEP_WORKSPACE[cr.new_path(rel)]
        release(self.src, {rel: "unreviewed source"})
        path = self.src / "MANIFEST.json"
        manifest = json.loads(path.read_text())
        manifest["files"][rel]["sha256"] = pinned
        path.write_text(json.dumps(manifest))
        code, log = run(self.src, self.out, self.ws)
        self.assertEqual(code, 0, log)
        self.assertIn(f"check: upstream changed {rel}", log)

    def test_reviewed_source_passes_with_stale_manifest_and_crlf(self):
        rel = ".agents/skills/adhd/SKILL.md"
        release(self.src, {rel: "reviewed\r\n"})
        with mock.patch.dict(cr.KEEP_WORKSPACE, {cr.new_path(rel): cr.sha(b"reviewed\n")}):
            code, log = run(self.src, self.out, self.ws)
        self.assertEqual(code, 0, log)
        self.assertNotIn(f"check: upstream changed {rel}", log)

    def test_replaced_upstream_skill_is_swapped_for_workspace_version(self):
        release(self.src, {"a.md": "x", ".agents/skills/drawio/SKILL.md": "upstream"})
        (self.src / ".agents/skills/drawio/scripts").mkdir(parents=True)
        (self.src / ".agents/skills/drawio/scripts/server.mjs").write_text("x")
        code, log = run(self.src, self.out, self.ws)
        self.assertEqual(code, 0, log)
        self.assertNotIn("warning:", log)
        self.assertIn("check: upstream changed .agents/skills/drawio/", log)
        self.assertEqual((self.out / ".claude/skills/drawio/SKILL.md").read_text(),
                         "workspace .claude/skills/drawio/SKILL.md")
        self.assertFalse((self.out / ".claude/skills/drawio/scripts/server.mjs").exists())

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
