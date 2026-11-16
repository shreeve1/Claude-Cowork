import datetime
import difflib
import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/map.py"


def extract_template(text):
    import re

    match = re.search(r"```markdown\s*\n(.*?)\n```", text, re.S)
    return match.group(1) + "\n" if match else text


spec = importlib.util.spec_from_file_location("map_script", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load {SCRIPT}")
map_script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = map_script
spec.loader.exec_module(map_script)


class MapTests(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, args)], text=True, capture_output=True
        )

    def make_map(
        self, folder, rows="| 1 | First | - | Todo | - |", status="active", next_text=None
    ):
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "map.md"
        next_text = (
            next_text
            or "### Stage 1: First\n- **Goal:** Do it\n- **Done when:** Verify it\n- **Starts from:** Inputs"
        )
        path.write_text(
            f"---\nstatus: {status}\ncreated: 2026-11-13\n---\n# Map\n\n## Destination\nA result.\n\n## Stages\n| # | Stage | Depends on | Status | Evidence |\n| --- | --- | --- | --- | --- |\n{rows}\n\n## Next\n{next_text}\n\n## Open questions\n- None\n\n## Decisions\n- None\n\n## Constraints\n- None\n\n## Found along the way\n- None\n\n## Log\n- 2026-11-13 Started.\n",
            encoding="utf-8",
        )
        return path

    def test_template_and_example_contract(self):
        for path in (ROOT / "references/template.md", ROOT / "references/example.md"):
            text = path.read_text()
            if path.name == "template.md":
                text = extract_template(text)
            with tempfile.TemporaryDirectory() as temp:
                target = pathlib.Path(temp) / "map.md"
                target.write_text(text)
                result = self.cli("audit", target)
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertIn("audit: 0 errors", result.stdout)

    def test_added_audit_contracts(self):
        cases = [
            ("created: bad", "created"),
            ("| 1 | First | - | Todo | extra | cell |", "escape a pipe"),
            (
                "### Stage 1: First\\n- **Goal:** x\\n- **Done when:** x\\n- **Starts from:** x",
                "Where it stopped",
            ),
            ("### Stage 1: First\\n- **Done when:** x\\n- **Starts from:** x", "Goal"),
            ("### Stage 1: First\\n- **Goal:** x\\n- **Starts from:** x", "Done when"),
            ("### Stage 1: First\\n- **Goal:** x\\n- **Done when:** x", "Starts from"),
        ]
        for snippet, expected in cases:
            with self.subTest(snippet=snippet), tempfile.TemporaryDirectory() as temp:
                path = self.make_map(pathlib.Path(temp), rows="| 1 | First | - | Active | - |")
                text = path.read_text()
                if snippet.startswith("created:"):
                    text = text.replace("created: 2026-11-13", snippet)
                elif snippet.startswith("|"):
                    text = text.replace("| 1 | First | - | Active | - |", snippet)
                else:
                    start = text.index("### Stage")
                    end = text.index("\n\n## Open questions")
                    snippet = snippet.replace("\\n", "\n")
                    text = text[:start] + snippet + text[end:]
                path.write_text(text)
                result = self.cli("audit", path)
                self.assertEqual(result.returncode, 1)
                self.assertIn(expected, result.stdout)
                if snippet.startswith("|"):
                    expected_line = text[: text.index(snippet)].count("\n") + 1
                    self.assertIn(f"line {expected_line}", result.stdout)

    def test_malformed_example_row_reports_file_line_number(self):
        example = ROOT / "references/example.md"
        with tempfile.TemporaryDirectory() as temp:
            target = pathlib.Path(temp) / "example.md"
            text = example.read_text()
            text = text.replace(
                "| 5 | Remove the old server | 4 | Todo | - |",
                "| 5 | Remove the old server | 4 | Todo |",
            )
            target.write_text(text)
            result = self.cli("audit", target)
            self.assertIn("line 20", result.stdout)

    def test_status_word_notes_allow_punctuation(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_map(
                pathlib.Path(temp),
                rows="| 1 | Dropped | - | Dropped: reason | - |",
                status="dropped",
                next_text="None",
            )
            path.write_text(path.read_text().replace("## Log", "## Outcome\nStopped.\n\n## Log"))
            audit = self.cli("audit", path)
            self.assertEqual(audit.returncode, 0, audit.stdout)
            self.assertNotIn("unknown status word", audit.stdout)

    def test_dropped_colon_without_reason_errors(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_map(
                pathlib.Path(temp), rows="| 1 | Dropped | - | Dropped: | - |", next_text="None"
            )
            path.write_text(path.read_text().replace("## Log", "## Outcome\nStopped.\n\n## Log"))
            result = self.cli("audit", path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Dropped without reason", result.stdout)

    def test_claim_ready_stage_commits_only_map(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            path = self.make_map(root / "docs/maps", rows="| 1 | First | - | Todo | - |")
            subprocess.run(["git", "config", "user.name", "T"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "t@x"], cwd=root, check=True)
            subprocess.run(["git", "add", str(path)], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            (root / "modified").write_text("modified")
            (root / "staged").write_text("staged")
            subprocess.run(["git", "add", "staged"], cwd=root, check=True)
            result = self.cli("claim", path, "1")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("claimed stage 1: Active", result.stdout)
            text = path.read_text()
            self.assertIn("| 1 | First | - | Active | - |", text)
            self.assertIn("**Where it stopped:** nothing yet (started ", text)
            self.assertIn("Stage 1 claimed.", text)
            changed = subprocess.check_output(
                ["git", "show", "--pretty=format:", "--name-only", "HEAD"], cwd=root, text=True
            )
            self.assertEqual(changed.strip(), "docs/maps/map.md")
            self.assertEqual(
                subprocess.check_output(["git", "status", "--short"], cwd=root, text=True).count(
                    "modified"
                ),
                1,
            )
            self.assertIn(
                "A  staged",
                subprocess.check_output(["git", "status", "--short"], cwd=root, text=True),
            )

    def test_claim_escaped_pipes_preserves_cells(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_map(
                pathlib.Path(temp),
                rows="| 1 | First | - | Todo | `repo@abc` |",
                next_text="### Stage 1: First\n- **Goal:** Fix a \\| b\n- **Done when:** Verify it\n- **Starts from:** Inputs",
            )
            text = path.read_text().replace(
                "| 1 | First | - | Todo | `repo@abc` |",
                "| 1 | Fix a \\| b | - | Todo | `repo\\|abc` |",
            )
            path.write_text(text)
            before = text.splitlines()
            result = self.cli("claim", path, "1")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            after = path.read_text().splitlines()
            self.assertTrue(
                any("| Fix a \\| b |" in line and "| Active |" in line for line in after)
            )
            self.assertTrue(any("repo\\|abc" in line for line in after))
            self.assertIn("audit: 0 errors", self.cli("audit", path).stdout)
            expected = before.copy()
            row_index = next(i for i, line in enumerate(expected) if line.startswith("| 1 |"))
            expected[row_index] = "| 1 | Fix a \\| b | - | Active | `repo\\|abc` |"
            claimed_at = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
            brief_end = next(
                i for i, line in enumerate(expected) if line.startswith("## Open questions")
            )
            if expected[brief_end - 1] == "":
                brief_end -= 1
            expected.insert(
                brief_end,
                f"- **Where it stopped:** nothing yet (started {claimed_at})",
            )
            log_index = next(i for i, line in enumerate(expected) if line == "## Log")
            expected.insert(
                log_index + 2,
                f"- {claimed_at} Stage 1 claimed.",
            )
            self.assertEqual(after, expected)

    def test_claim_middle_row_changes_only_expected_lines(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_map(
                pathlib.Path(temp),
                rows="| 1 | First | - | Done | `repo@abc` |\n| 2 | Middle | 1 | Todo | - |\n| 3 | Last | 1 | Todo | - |",
                next_text="### Stage 2: Middle\n- **Goal:** Do it\n- **Done when:** Verify it\n- **Starts from:** Inputs\n### Stage 3: Last\n- **Goal:** Do it\n- **Done when:** Verify it\n- **Starts from:** Inputs",
            )
            before = path.read_text().splitlines()
            result = self.cli("claim", path, "2")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            after = path.read_text().splitlines()
            expected = before.copy()
            row_index = next(i for i, line in enumerate(expected) if line.startswith("| 2 |"))
            expected[row_index] = "| 2 | Middle | 1 | Active | - |"
            claimed_at = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
            brief_end = next(
                i for i, line in enumerate(expected) if line.startswith("### Stage 3:")
            )
            expected.insert(
                brief_end,
                f"- **Where it stopped:** nothing yet (started {claimed_at})",
            )
            log_index = next(i for i, line in enumerate(expected) if line == "## Log")
            expected.insert(
                log_index + 2,
                f"- {claimed_at} Stage 2 claimed.",
            )
            self.assertEqual(
                after,
                expected,
                "unexpected map lines changed:\n" + "\n".join(difflib.unified_diff(before, after)),
            )

    def test_claim_refusals_keep_bytes_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            cases = [
                ("| 1 | First | - | Done | `repo@abc` |", "1", "cannot claim"),
                ("| 1 | First | - | Dropped: reason | - |", "1", "cannot claim"),
                (
                    "| 1 | First | 2 | Todo | - |\n| 2 | Second | - | Todo | - |",
                    "1",
                    "waits on",
                ),
            ]
            for index, (rows, stage_id, expected) in enumerate(cases):
                next_text = (
                    "### Stage 2: Second\n- **Goal:** Do it\n- **Done when:** Verify it\n- **Starts from:** Inputs"
                    if index == 2
                    else "None"
                )
                path = self.make_map(root / str(index), rows=rows, next_text=next_text)
                before = path.read_bytes()
                result = self.cli("claim", path, stage_id)
                self.assertEqual(result.returncode, 1)
                self.assertIn(expected, result.stdout)
                self.assertEqual(path.read_bytes(), before)
            path = self.make_map(root / "unknown")
            before = path.read_bytes()
            result = self.cli("claim", path, "999")
            self.assertEqual(result.returncode, 1)
            self.assertIn("unknown stage id", result.stdout)
            self.assertEqual(path.read_bytes(), before)

    def test_claim_commit_failure_requires_manual_commit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "config", "user.name", "T"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "t@x"], cwd=root, check=True)
            path = self.make_map(root / "docs/maps")
            subprocess.run(["git", "add", str(path)], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            subprocess.run(["git", "config", "commit.gpgsign", "true"], cwd=root, check=True)
            subprocess.run(
                ["git", "config", "user.signingkey", "/no/such/key"], cwd=root, check=True
            )
            failed = self.cli("claim", path, "1")
            self.assertEqual(failed.returncode, 1)
            self.assertIn("NOT committed", failed.stdout)
            self.assertIn("before doing stage work", failed.stdout)
            rerun = self.cli("claim", path, "1")
            self.assertEqual(rerun.returncode, 1)
            self.assertIn("map has uncommitted changes", rerun.stdout)

    def test_claim_dirty_map_refuses_without_edit_or_commit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "config", "user.name", "T"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "t@x"], cwd=root, check=True)
            path = self.make_map(
                root / "docs/maps",
                rows="| 1 | First | - | Todo | - |\n| 2 | Second | - | Todo | - |",
                next_text="### Stage 1: First\n- **Goal:** Do it\n- **Done when:** Verify it\n- **Starts from:** Inputs\n### Stage 2: Second\n- **Goal:** Do it\n- **Done when:** Verify it\n- **Starts from:** Inputs",
            )
            subprocess.run(["git", "add", str(path)], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            path.write_text(
                path.read_text().replace(
                    "| 2 | Second | - | Todo | - |", "| 2 | Second | - | Waiting: editing | - |"
                )
            )
            before = path.read_bytes()
            head = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True
            ).strip()
            result = self.cli("claim", path, "1")
            self.assertEqual(result.returncode, 1)
            self.assertIn("map has uncommitted changes", result.stdout)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(
                subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
                head,
            )

    def test_claim_already_active_and_audit_error(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            active = self.make_map(
                root / "active",
                rows="| 1 | First | - | Active | - |",
                next_text="### Stage 1: First\n- **Goal:** Do it\n- **Done when:** Verify it\n- **Starts from:** Inputs\n- **Where it stopped:** in progress",
            )
            before = active.read_bytes()
            result = self.cli("claim", active, "1")
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("already Active", result.stdout)
            self.assertEqual(active.read_bytes(), before)
            broken = self.make_map(root / "broken").with_name("bad.md")
            broken.write_text(
                self.make_map(root / "broken")
                .read_text()
                .replace("created: 2026-11-13", "created: bad")
            )
            before = broken.read_bytes()
            result = self.cli("claim", broken, "1")
            self.assertEqual(result.returncode, 1)
            self.assertIn("audit first", result.stdout)
            self.assertEqual(broken.read_bytes(), before)

    def test_claim_crlf_and_untracked_map(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            path = self.make_map(root / "docs/maps", rows="| 1 | First | - | Todo | - |")
            path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
            subprocess.run(["git", "config", "user.name", "T"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "t@x"], cwd=root, check=True)
            subprocess.run(["git", "add", str(path)], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            result = self.cli("claim", path, "1")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn(b"\n", path.read_bytes().replace(b"\r\n", b""))
            changed = subprocess.check_output(
                ["git", "show", "--pretty=format:", "--name-only", "HEAD"], cwd=root, text=True
            )
            self.assertEqual(changed.strip(), "docs/maps/map.md")

    def test_claim_waiting_preserves_where_and_outside_git_edits(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_map(
                pathlib.Path(temp),
                rows="| 1 | First | - | Waiting: on James | - |",
                next_text="### Stage 1: First\n- **Goal:** Do it\n- **Done when:** Verify it\n- **Starts from:** Inputs\n- **Where it stopped:** draft ready",
            )
            old = "- **Where it stopped:** draft ready"
            result = self.cli("claim", path, "1")
            self.assertEqual(result.returncode, 0, result.stdout)
            text = path.read_text()
            self.assertIn(old, text)
            self.assertIn("| 1 | First | - | Active | - |", text)
            self.assertIn("not in git", result.stdout)

    def test_dropped_map_and_dropped_stage_reason(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_map(
                pathlib.Path(temp),
                status="dropped",
                next_text="None",
                rows="| 1 | Dropped | - | Dropped | reason recorded |",
            )
            path.write_text(
                path.read_text().replace("## Log", "## Outcome\nStopped by owner.\n\n## Log")
            )
            result = self.cli("audit", path)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_status_edge_cases(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            empty = self.cli("status", root).stdout
            self.assertIn("no maps under", empty)
            missing = self.cli("status", root / "missing").stdout
            self.assertIn("no such path", missing)
            maps = root / "docs/maps"
            maps.mkdir(parents=True)
            (maps / "corrupt.md").write_text("not a map", encoding="utf-8")
            corrupt = self.cli("status", root).stdout
            self.assertIn("(13 errors: run audit)", corrupt)

    def test_ready_finish_and_paused_status(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            active = self.make_map(
                root / "active",
                status="active",
                rows="| 1 | Done | - | Done | `repo@abc` |",
                next_text="None",
            )
            self.assertIn("ready to finish", self.cli("audit", active).stdout)
            paused = self.make_map(root / "paused", status="paused")
            result = self.cli("status", paused)
            self.assertIn("[paused]", result.stdout)
            self.assertIn(str(paused), result.stdout)

    def test_size_warning(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_map(pathlib.Path(temp))
            path.write_text(path.read_text() + "\n" + "detail\n" * 260)
            self.assertIn("over 250 lines", self.cli("audit", path).stdout)

    def test_errors(self):
        cases = [
            ("status: invalid", "frontmatter"),
            ("# Map\n", "title"),
            ("## Stages", "Stages"),
            ("A result.", "Destination"),
            ("| # | Stage | Depends on | Status | Evidence |", "Stages"),
        ]
        for snippet, expected in cases:
            with self.subTest(snippet=snippet), tempfile.TemporaryDirectory() as temp:
                path = self.make_map(pathlib.Path(temp))
                text = path.read_text()
                if snippet.startswith("status:"):
                    text = text.replace("status: active", snippet)
                elif snippet == "# Map\n":
                    text = text.replace(snippet, "")
                elif snippet == "## Stages":
                    text = text.replace(snippet, "## Wrong")
                elif snippet == "A result.":
                    text = text.replace(snippet, "")
                else:
                    text = text.replace(snippet, "| wrong |")
                path.write_text(text)
                result = self.cli("audit", path)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn(expected.lower(), result.stdout.lower())

    def test_stage_errors_and_cycle(self):
        cases = [
            ("| 1 | First | - | Strange | - |", "stage 1"),
            ("| 1 | First | 8 | Todo | - |", "stage 1"),
            ("| 1 | First | - | Done | - |", "stage 1"),
            ("| 1 | First | - | Waiting | - |", "stage 1"),
            ("| 1 | First | - | Dropped | - |", "stage 1"),
            ("| 1 | First | - |  | - |", "stage 1"),
            ("| x | First | - | Todo | - |", "stage x"),
            ("| 1 | First | - | Todo | - |\n| 1 | Again | - | Todo | - |", "duplicate"),
            ("| 1 | First | 2 | Todo | - |\n| 2 | Second | 1 | Todo | - |", "cycle"),
        ]
        for rows, expected in cases:
            with self.subTest(rows=rows), tempfile.TemporaryDirectory() as temp:
                next_text = "None" if "| Done |" in rows or "| Waiting |" in rows else None
                path = self.make_map(pathlib.Path(temp), rows=rows, next_text=next_text)
                result = self.cli("audit", path)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn(expected, result.stdout)

    def test_missing_brief_done_when_and_done_map(self):
        for status, next_text, expected in [
            ("active", "None", "stage 1"),
            ("active", "### Stage 1: First\n- **Goal:** x", "Done when"),
            ("done", "None", "status"),
        ]:
            with self.subTest(status=status), tempfile.TemporaryDirectory() as temp:
                path = self.make_map(pathlib.Path(temp), status=status, next_text=next_text)
                result = self.cli("audit", path)
                self.assertEqual(result.returncode, 1)
                self.assertIn(expected, result.stdout)

    def test_untracked_map_warns(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            path = self.make_map(root)
            result = self.cli("audit", path)
            self.assertIn("untracked", result.stdout.lower())

    def test_repo_relative_missing_path_warns(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            path = self.make_map(root, rows="| 1 | First | - | Todo | `missing/file.md` |")
            self.assertIn("path does not exist", self.cli("audit", path).stdout)

    def test_log_warnings_and_only_placeholder_text(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_map(
                pathlib.Path(temp),
                rows="| 1 | First | - | Active | - |",
                next_text="### Stage 1: First\n- **Goal:** x\n- **Done when:** x\n- **Starts from:** x\n- **Where it stopped:** x",
            )
            text = path.read_text().replace("- 2026-11-13 Started.", "- Started <Today>.")
            path.write_text(text)
            output = self.cli("audit", path).stdout
            self.assertIn("Log bullet without", output)
            self.assertIn("placeholder", output)
            path.write_text(path.read_text().replace("<Today>", "today"))
            self.assertNotIn("placeholders", self.cli("audit", path).stdout)
            path.write_text(
                path.read_text().replace("- today.", "").replace("- Started today.", "")
            )
            self.assertIn("Log is empty", self.cli("audit", path).stdout)

    def test_dependency_and_brief_warnings(self):
        with tempfile.TemporaryDirectory() as temp:
            rows = "| 1 | Dropped | - | Dropped because obsolete | - |\n| 2 | Active | 1 | Active | - |\n| 3 | Done | 2 | Done | `repo@abc` |\n| 4 | Parent | - | Done | `repo@abc` |\n| 5 | Later | 4 | Todo | - |"
            path = self.make_map(
                pathlib.Path(temp),
                rows=rows,
                next_text="### Stage 5: Later\n- **Done when:** x\n- **Goal:** x",
            )
            output = self.cli("audit", path).stdout
            self.assertIn("Dropped stage", output)
            self.assertIn("dependencies not Done", output)
            self.assertIn("frontier stage has no brief", output)

    def test_git_commit_drift_and_clean_outside_git(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            maps = root / "docs/maps"
            path = self.make_map(
                maps, rows="| 1 | Done stage | - | Done | `abcdef0` |", next_text="None"
            )
            repo_marker = root / ".git"
            self.assertTrue(repo_marker.is_dir())
            subprocess.run(["git", "add", "."], cwd=root, check=True)

            def commit(*args):
                subprocess.run(
                    ["git", "-c", "user.name=T", "-c", "user.email=t@x", "commit", *args],
                    cwd=root,
                    check=True,
                )

            commit("-qm", "map")
            sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            path.write_text(path.read_text().replace("abcdef0", sha[:8]))
            subprocess.run(["git", "add", str(path)], cwd=root, check=True)
            commit("-qm", "map update")
            commit("--allow-empty", "-qm", "after map")
            result = self.cli("audit", path)
            self.assertIn("1 commits since the map last changed", result.stdout)
            self.assertNotIn("not found", result.stdout)
            path.write_text(path.read_text() + "\nedit\n")
            self.assertIn("uncommitted", self.cli("audit", path).stdout)
            outside_dir = tempfile.TemporaryDirectory()
            self.addCleanup(outside_dir.cleanup)
            outside = pathlib.Path(outside_dir.name) / "map.md"
            outside.write_text(path.read_text())
            self.assertIn(
                "note: commit, drift and path checks skipped", self.cli("audit", outside).stdout
            )

    def test_commit_range_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            path = self.make_map(
                root, rows="| 1 | Done stage | - | Done | `abcdef0..1234567` |", next_text="None"
            )
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(
                ["git", "-c", "user.name=T", "-c", "user.email=t@x", "commit", "-qm", "base"],
                cwd=root,
                check=True,
            )
            result = self.cli("audit", path)
            self.assertIn("stage 1", result.stdout)
            self.assertIn("not found", result.stdout)

    def test_bad_and_foreign_commit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            path = self.make_map(
                root,
                rows="| 1 | Done stage | - | Done | `foreign@deadbee` `abcdef0` |",
                next_text="None",
            )
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(
                ["git", "-c", "user.name=T", "-c", "user.email=t@x", "commit", "-qm", "base"],
                cwd=root,
                check=True,
            )
            result = self.cli("audit", path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("stage 1", result.stdout)
            self.assertIn("repo@sha", result.stdout)

    def test_status_and_frontier(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            maps = root / "docs/maps"
            path = self.make_map(
                maps,
                rows="| 1 | Active stage | - | Active | - |\n| 2 | Ready stage | - | Todo | - |\n| 3 | Waiting stage | - | Waiting on James | - |",
                next_text="### Stage 1: First\n- **Done when:** x",
            )
            audit = self.cli("audit", path).stdout
            self.assertLess(audit.index("1 Active stage"), audit.index("2 Ready stage"))
            self.assertLess(audit.index("2 Ready stage"), audit.index("3 Waiting stage"))
            status = self.cli("status", root).stdout
            for word in (
                "Active stage",
                "Ready stage",
                "Waiting stage",
                "open questions: 0",
                "James",
            ):
                self.assertIn(word, status)

    def test_status_hides_done_and_accepts_multiple_roots(self):
        with tempfile.TemporaryDirectory() as temp:
            base = pathlib.Path(temp)
            roots = [base / "one", base / "two"]
            for root in roots:
                maps = root / "docs/maps"
                self.make_map(
                    maps,
                    status="done",
                    rows="| 1 | Done stage | - | Done | `repo@abc` |",
                    next_text="None",
                )
                (maps / "map.md").write_text(
                    (maps / "map.md").read_text().replace("# Map", "# Map\\nDone stage")
                )
            hidden = self.cli("status", *roots).stdout
            shown = self.cli("status", "--all", *roots).stdout
            self.assertNotIn("Done stage", hidden)
            self.assertIn("Done stage", shown)

    def test_skill_links_and_missing_file(self):
        import re

        for link in re.findall(r"\]\((references/[^)]+\.md)\)", (ROOT / "SKILL.md").read_text()):
            self.assertTrue((ROOT / link).is_file())
        self.assertEqual(self.cli("audit", "/missing/map.md").returncode, 2)


if __name__ == "__main__":
    unittest.main()
