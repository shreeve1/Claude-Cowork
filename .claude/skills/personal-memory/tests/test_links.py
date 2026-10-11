"""gate.py links/backlinks over the memory note link graph: broken links and orphans."""
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_indexes import GATE, INDEXES, make_index, make_schema, run_script  # noqa: E402


def memory_with(*files):
    """Tempdir with a valid index/schema and the given (relpath-from-memory, body) notes."""
    root = Path(tempfile.mkdtemp())
    mem = root / "memory"
    mem.mkdir()
    make_index(mem)
    make_schema(mem)
    for d in ("workflows", "decisions"):
        (mem / d).mkdir()
    run_script(INDEXES, mem)
    for rel, body in files:
        p = mem / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
        with open(mem / "index.md", "a", encoding="utf-8") as f:
            f.write(f"| [{p.stem}](memory/{rel}) | note | x | 2026-10-07 |\n")
    return mem


class LinksTests(unittest.TestCase):
    def test_backlinks_and_none(self):
        mem = memory_with(
            ("guides/a.md", "see ](memory/guides/b.md) here\n"),
            ("guides/b.md", "b\n"),
        )
        (mem / "guides" / "unlisted.md").write_text("u\n", encoding="utf-8")
        out = run_script(GATE, mem, "backlinks", "memory/guides/b.md").stdout
        self.assertEqual(out, "- memory/guides/a.md\n- memory/index.md\n")
        out = run_script(GATE, mem, "backlinks", "memory/guides/unlisted.md").stdout
        self.assertEqual(out, "none\n")

    def test_anchor_resolves_to_note(self):
        mem = memory_with(
            ("guides/a.md", "see ](memory/guides/b.md#section)\n"),
            ("guides/b.md", "b\n"),
        )
        self.assertEqual(run_script(GATE, mem, "backlinks", "memory/guides/b.md").stdout,
                         "- memory/guides/a.md\n- memory/index.md\n")

    def test_backticked_path_counts(self):
        mem = memory_with(
            ("rules.md", "load `memory/preferences/tone.md`\n"),
            ("preferences/tone.md", "tone\n"),
        )
        self.assertEqual(run_script(GATE, mem, "backlinks", "memory/preferences/tone.md").stdout,
                         "- memory/index.md\n- memory/rules.md\n")

    def test_index_and_hub_links_do_not_count(self):
        mem = memory_with(
            ("guides/x.md", "x\n"),
            ("guides/index.md", "see ](memory/guides/x.md)\n"),
            ("_hubs/acme.md", "see ](memory/guides/x.md)\n"),
        )
        out = run_script(GATE, mem, "links").stdout
        self.assertIn("No inbound links:\n- memory/guides/x.md\n", out)
        self.assertNotIn("Broken links:", out)

    def test_hub_only_note_is_isolated_but_backlinks_shows_the_hub(self):
        mem = memory_with(
            ("guides/x.md", "x\n"),
            ("guides/index.md", "see ](memory/guides/x.md)\n"),
            ("_hubs/acme.md", "see ](memory/guides/x.md)\n"),
        )
        out = run_script(GATE, mem, "backlinks", "memory/guides/x.md").stdout
        self.assertEqual(out, "- memory/_hubs/acme.md\n- memory/guides/index.md\n- memory/index.md\n")
        links_out = run_script(GATE, mem, "links").stdout
        self.assertIn("No inbound links:\n- memory/guides/x.md\n", links_out)

    def test_broken_link_reported_without_failing_audit(self):
        mem = memory_with(
            ("guides/a.md", "see ](memory/guides/missing.md)\n"),
            ("guides/b.md", "b\n"),
        )
        out = run_script(GATE, mem, "links").stdout
        self.assertIn("Broken links:\n- memory/guides/a.md -> memory/guides/missing.md\n", out)
        proc = run_script(GATE, mem, "audit")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("Warning: memory/guides/a.md: broken link memory/guides/missing.md", proc.stdout)

    def test_no_outgoing_and_self_link_ignored(self):
        mem = memory_with(
            ("guides/a.md", "only myself: ](memory/guides/a.md)\n"),
            ("guides/b.md", "b\n"),
        )
        out = run_script(GATE, mem, "links").stdout
        self.assertIn("No outgoing links:\n- memory/guides/a.md\n- memory/guides/b.md\n", out)

    def test_placeholder_and_glob_paths_are_not_links(self):
        mem = memory_with(
            ("guides/a.md", "shape `memory/workflows/<topic>/<slug>.md` and ](memory/preferences/*.md)\n"),
            ("guides/b.md", "b\n"),
        )
        out = run_script(GATE, mem, "links").stdout
        self.assertNotIn("Broken links:", out)
        self.assertIn("links: 2 notes, 0 broken, 2 no outgoing, 2 no inbound\n", out)

    def test_parent_dir_and_non_note_targets_are_not_links(self):
        mem = memory_with(
            ("guides/a.md", "](memory/../../outside.md) `memory/../x.md` ](memory/workflows) ](memory/logo.png)\n"),
            ("guides/b.md", "b\n"),
        )
        out = run_script(GATE, mem, "links").stdout
        self.assertNotIn("Broken links:", out)
        self.assertIn("links: 2 notes, 0 broken, 2 no outgoing, 2 no inbound\n", out)


if __name__ == "__main__":
    unittest.main()
