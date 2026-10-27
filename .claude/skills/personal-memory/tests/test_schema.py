"""Unit tests for schema.py: the memory Schema loader (contract 3)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import schema


def write_schema(memory_dir, **overrides):
    data = {
        "client_subjects": ["halo", "365"],
        "topics": ["halo", "365"],
        "topic_dirs": ["workflows", "decisions"],
        "client_dirs": ["tickets", "projects", "procedures", "meetings", "templates"],
    }
    data.update(overrides)
    (memory_dir / "schema.json").write_text(json.dumps(data), encoding="utf-8")


class SchemaLoadTests(unittest.TestCase):
    def test_load_returns_schema_dict(self):
        with tempfile.TemporaryDirectory() as td:
            mem = Path(td)
            write_schema(mem, client_subjects=["halo", "cloud"])
            data = schema.load(mem)
            self.assertEqual(data["client_subjects"], ["halo", "cloud"])
            self.assertEqual(data["topics"], ["halo", "365"])
            self.assertEqual(data["topic_dirs"], ["workflows", "decisions"])
            self.assertEqual(data["client_dirs"][0], "tickets")

    def test_missing_file_error_names_path(self):
        with tempfile.TemporaryDirectory() as td:
            mem = Path(td)
            with self.assertRaises(SystemExit) as cm:
                schema.load(mem)
            msg = str(cm.exception)
            self.assertIn("schema.json", msg)
            self.assertIn("not found", msg)
            self.assertIn(str(mem), msg)

    def test_missing_key_error_names_path_and_key(self):
        with tempfile.TemporaryDirectory() as td:
            mem = Path(td)
            (mem / "schema.json").write_text(
                json.dumps({"client_subjects": ["halo"]}), encoding="utf-8"
            )
            with self.assertRaises(SystemExit) as cm:
                schema.load(mem)
            msg = str(cm.exception)
            self.assertIn("schema.json", msg)
            self.assertIn("topics", msg)
            self.assertIn("topic_dirs", msg)

    def test_invalid_json_error_names_path(self):
        with tempfile.TemporaryDirectory() as td:
            mem = Path(td)
            (mem / "schema.json").write_text("{nope", encoding="utf-8")
            with self.assertRaises(SystemExit) as cm:
                schema.load(mem)
            self.assertIn("schema.json", str(cm.exception))

    def test_client_folder_defaults_to_clients(self):
        with tempfile.TemporaryDirectory() as td:
            mem = Path(td)
            write_schema(mem)
            self.assertEqual(schema.load(mem)["client_folder"], "clients")

    def test_client_folder_is_read_from_schema(self):
        with tempfile.TemporaryDirectory() as td:
            mem = Path(td)
            write_schema(mem, client_folder="students")
            self.assertEqual(schema.load(mem)["client_folder"], "students")

    def test_bad_client_folder_names_the_problem(self):
        for bad in ("Students", "my students", "../x", "", 5, "memory", "research", "docs"):
            with self.subTest(bad=bad), tempfile.TemporaryDirectory() as td:
                mem = Path(td)
                write_schema(mem, client_folder=bad)
                with self.assertRaises(SystemExit) as cm:
                    schema.load(mem)
                self.assertIn("client_folder", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
