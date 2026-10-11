"""Tests for personal-memory client hubs: procedures folder is listed like tickets/projects."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hubs


def make_schema(memory_dir, client_subjects=None):
    """Minimal memory/schema.json; subjects default to the canonical list."""
    (memory_dir / "schema.json").write_text(json.dumps({
        "client_subjects": client_subjects if client_subjects is not None
        else ["halo", "365", "3cx", "network", "backup", "security", "endpoints",
              "contacts", "temperature"],
        "topics": ["workflows"],
        "topic_dirs": ["workflows"],
        "client_dirs": ["tickets", "projects", "procedures", "meetings", "templates"],
    }), encoding="utf-8")


class HubProcedureTests(unittest.TestCase):
    def test_client_hub_lists_procedures(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            mem = root / "memory"
            note = mem / "clients/halo/exampleco"
            note.mkdir(parents=True)
            make_schema(mem)
            (note / "note.md").write_text("---\ntitle: Note\n---\n")
            proc = root / "clients/exampleco/procedures/365"
            proc.mkdir(parents=True)
            (proc / "mail-backup.md").write_text("# x\n")
            wanted, _ = hubs.plan(mem)
            hub = mem / "clients/_hubs/exampleco.md"
            text = wanted[hub]
            self.assertIn("## procedures\n", text)
            self.assertIn("- [mail-backup](clients/exampleco/procedures/365/mail-backup.md)", text)

    def test_hub_sections_follow_schema_order_then_unknown_subjects(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            mem = root / "memory"
            for subject in ("halo", "temperature", "vpn"):
                (mem / f"clients/{subject}/abx").mkdir(parents=True)
                (mem / f"clients/{subject}/abx/note.md").write_text(f"---\ntitle: {subject}\n---\n")
            make_schema(mem, client_subjects=["temperature", "halo"])
            wanted, _ = hubs.plan(mem)
            text = wanted[mem / "clients/_hubs/abx.md"]
            self.assertLess(text.index("## temperature"), text.index("## halo"))
            self.assertLess(text.index("## halo"), text.index("## vpn"))

    def test_configured_client_folder_holds_notes_hubs_and_documents(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            mem = root / "memory"
            (mem / "students/contacts/ana").mkdir(parents=True)
            make_schema(mem)
            data = json.loads((mem / "schema.json").read_text(encoding="utf-8"))
            data["client_folder"] = "students"
            (mem / "schema.json").write_text(json.dumps(data), encoding="utf-8")
            (mem / "students/contacts/ana/note.md").write_text("---\ntitle: Note\n---\n")
            (mem / "clients/contacts/old").mkdir(parents=True)
            (mem / "clients/contacts/old/ignored.md").write_text("---\ntitle: Ignored\n---\n")
            proc = root / "students/ana/procedures/pickup"
            proc.mkdir(parents=True)
            (proc / "late.md").write_text("# x\n")
            wanted, _ = hubs.plan(mem)
            self.assertEqual(sorted(p.relative_to(mem).as_posix() for p in wanted), ["students/_hubs/ana.md"])
            text = wanted[mem / "students/_hubs/ana.md"]
            self.assertIn("- [Note](memory/students/contacts/ana/note.md)", text)
            self.assertIn("- [late](students/ana/procedures/pickup/late.md)", text)


if __name__ == "__main__":
    unittest.main()
