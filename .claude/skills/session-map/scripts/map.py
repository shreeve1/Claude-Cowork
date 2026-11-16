#!/usr/bin/env python3
"""Mechanical status and consistency checks for session maps."""

import argparse
import datetime
import pathlib
import re
import shutil
import subprocess
import sys

HEADER = ["#", "Stage", "Depends on", "Status", "Evidence"]
STATES = {"todo", "active", "waiting", "done", "dropped"}


def visible_text(text):
    """Blank fenced-code lines while retaining line numbers."""
    lines = text.splitlines(keepends=True)
    fenced = False
    result = []
    for line in lines:
        if line.lstrip().startswith("```"):
            fenced = not fenced
            result.append("\n" if line.endswith("\n") else "")
        elif fenced:
            result.append("\n" if line.endswith("\n") else "")
        else:
            result.append(line)
    return "".join(result)


def split_cells(line):
    cells, current = [], []
    escaped = False
    for char in line.strip().strip("|"):
        if char == "|" and not escaped:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        escaped = char == "\\" and not escaped
        if char != "\\":
            escaped = False
    cells.append("".join(current).strip())
    return cells


def parse(path):
    text = path.read_text(encoding="utf-8-sig")
    visible = visible_text(text)
    front = re.search(r"^---\s*\n(.*?)\n---", visible, re.M | re.S)
    status_match = re.search(r"^status:\s*(\S+)", front.group(1), re.M) if front else None
    created_match = re.search(r"^created:\s*(\S+)", front.group(1), re.M) if front else None
    title_match = re.search(r"^#\s+(.+)$", visible, re.M)
    sections = {
        name: body
        for name, body in re.findall(r"^##\s+(.+?)\s*\n(.*?)(?=^##\s+|\Z)", visible, re.M | re.S)
    }
    stage_rows, row_errors = [], []
    in_stages = False
    for line_number, line in enumerate(visible.splitlines(), 1):
        if re.match(r"^##\s+", line):
            in_stages = line.strip() == "## Stages"
            continue
        if not in_stages or not line.lstrip().startswith("|"):
            continue
        cells = split_cells(line)
        if cells == HEADER or all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            continue
        if len(cells) != 5:
            row_errors.append((line_number, line.strip()))
            continue
        stage_rows.append(
            dict(zip(("id", "title", "deps", "status", "evidence"), cells, strict=True))
        )
    briefs_list = list(
        re.finditer(
            r"^### Stage\s+(\S+):.*?$\n(.*?)(?=^### |\Z)", sections.get("Next", ""), re.M | re.S
        )
    )
    briefs = {}
    for brief in briefs_list:
        briefs.setdefault(brief.group(1), []).append(brief.group(2))
    return {
        "text": text,
        "visible": visible,
        "status": status_match.group(1).lower() if status_match else "",
        "created": created_match.group(1) if created_match else "",
        "title": title_match.group(1) if title_match else "(untitled)",
        "sections": sections,
        "stages": stage_rows,
        "row_errors": row_errors,
        "briefs": briefs,
    }


def rebuild_row(cells, newline, has_line_ending):
    row = "| " + " | ".join(cells) + " |"
    return row + newline if has_line_ending else row


def state(stage):
    match = re.match(r"([A-Za-z]+)", stage["status"].lstrip())
    return match.group(1).lower() if match else ""


def note(stage):
    status = stage["status"].lstrip()
    match = re.match(r"[A-Za-z]+", status)
    return status[match.end() :].lstrip(" :;,-") if match else ""


def dependencies(stage):
    return [] if stage["deps"] == "-" else [item.strip() for item in stage["deps"].split(",")]


def readiness(stages):
    by_id = {stage["id"]: stage for stage in stages}

    def ready(stage):
        return all(dep in by_id and state(by_id[dep]) == "done" for dep in dependencies(stage))

    active = [stage for stage in stages if state(stage) == "active"]
    ready_stages = [stage for stage in stages if state(stage) == "todo" and ready(stage)]
    waiting = [stage for stage in stages if state(stage) == "waiting"]
    return by_id, ready, active, ready_stages, waiting


def evidence_has_proof(evidence):
    return bool(re.search(r"`[^`]+`|https?://\S+", evidence))


def check(path, *, git_checks=True):
    findings = []

    def error(area, message):
        findings.append(("ERROR", area, message))

    def warn(area, message):
        findings.append(("WARN", area, message))

    try:
        data = parse(path)
    except (OSError, UnicodeError) as exc:
        return [("ERROR", "file", str(exc))], None
    status, sections, stages, briefs = (
        data["status"],
        data["sections"],
        data["stages"],
        data["briefs"],
    )
    if status not in {"active", "paused", "done", "dropped"}:
        error("frontmatter", "missing or invalid status")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data["created"]):
        error("frontmatter", "created missing or invalid; expected YYYY-MM-DD")
    if data["title"] == "(untitled)":
        error("title", "missing level-one title")
    for number, line in data["row_errors"]:
        error(
            "Stages",
            f"line {number} does not have 5 cells: {line!r}; escape a pipe inside a cell as \\|",
        )
    required = (
        "Destination",
        "Stages",
        "Next",
        "Open questions",
        "Decisions",
        "Constraints",
        "Found along the way",
        "Log",
    )
    for section in required:
        if section not in sections:
            error(section, "required section missing")
    if not sections.get("Destination", "").strip():
        error("Destination", "empty")
    if "| # | Stage | Depends on | Status | Evidence |" not in sections.get("Stages", ""):
        error("Stages", "table missing or wrong header")
    ids = [stage["id"] for stage in stages]
    if len(ids) != len(set(ids)):
        error("Stages", "duplicate stage id")
    for stage in stages:
        sid, current = stage["id"], state(stage)
        if not re.fullmatch(r"\d+[a-z]?", sid):
            error(f"stage {sid}", "malformed stage id")
        if not current or current not in STATES:
            error(f"stage {sid}", "unknown status word")
        deps = dependencies(stage)
        if any(not re.fullmatch(r"\d+[a-z]?", dep) or dep not in ids for dep in deps):
            error(f"stage {sid}", "Depends on unknown or malformed id")
        if current == "done" and stage["evidence"].strip() in {"", "-"}:
            error(f"stage {sid}", "Done without evidence")
        if current == "done" and not evidence_has_proof(stage["evidence"]):
            warn(f"stage {sid}", "Done evidence has no commit, path or URL")
        if current == "waiting" and not note(stage) and stage["evidence"].strip() in {"", "-"}:
            error(f"stage {sid}", "Waiting without note or evidence")
        if current == "dropped" and not note(stage) and stage["evidence"].strip() in {"", "-"}:
            error(f"stage {sid}", "Dropped without reason")
    by_id, ready, active, ready_stages, waiting = readiness(stages)

    def visit(sid, visiting, visited):
        if sid in visiting:
            return True
        if sid in visited:
            return False
        visiting.add(sid)
        found = any(
            dep in by_id and visit(dep, visiting, visited) for dep in dependencies(by_id[sid])
        )
        visiting.remove(sid)
        visited.add(sid)
        return found

    if any(visit(sid, set(), set()) for sid in by_id):
        error("Stages", "dependency cycle")

    for sid in briefs:
        chunks = briefs[sid]
        if len(chunks) > 1:
            error(f"stage {sid}", "duplicate brief")
        if sid not in by_id:
            warn("Next", f"brief for unknown stage {sid}")
        for brief in chunks:
            for field in ("Goal", "Done when", "Starts from"):
                if f"**{field}:**" not in brief:
                    error(f"stage {sid}", f"brief missing **{field}:**")
    for stage in stages:
        sid, current = stage["id"], state(stage)
        deps = [by_id[dep] for dep in dependencies(stage) if dep in by_id]
        if (current == "active" or (current == "todo" and ready(stage))) and sid not in briefs:
            error(f"stage {sid}", "frontier stage has no brief")
        if current == "active" and "**Where it stopped:**" not in "\n".join(briefs.get(sid, [])):
            error(f"stage {sid}", "Active brief missing **Where it stopped:**")
        if current in {"active", "done"} and any(state(dep) != "done" for dep in deps):
            warn(f"stage {sid}", "Active or Done stage has dependencies not Done")
        if any(state(dep) == "dropped" for dep in deps):
            warn(f"stage {sid}", "depends on a Dropped stage")
    for sid in briefs:
        stage = by_id.get(sid)
        if stage and (
            state(stage) in {"done", "dropped"} or (state(stage) == "todo" and not ready(stage))
        ):
            warn(f"stage {sid}", "brief is not for a current frontier stage")

    for map_status in ("done", "dropped"):
        if status == map_status and (
            any(state(stage) in {"todo", "active", "waiting"} for stage in stages)
            or "Outcome" not in sections
        ):
            error("status", f"{map_status} map has unfinished stages or no Outcome")
    placeholder_text = re.sub(r"<!--.*?-->|`[^`]*`", "", data["visible"], flags=re.S)
    if re.search(r"<[A-Z][^<>\n]*>", placeholder_text):
        warn("placeholders", "unfilled template placeholder")
    if len(data["text"].splitlines()) > 250:
        warn("size", "map over 250 lines")

    git_available = shutil.which("git") is not None
    repo_result = (
        subprocess.run(
            ["git", "-C", str(path.resolve().parent), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
        )
        if git_available
        else None
    )
    in_repo = bool(repo_result and repo_result.returncode == 0)
    repo = pathlib.Path(repo_result.stdout.strip()) if repo_result is not None and in_repo else None
    if not in_repo:
        if git_checks:
            findings.append(("note", "git", "commit, drift and path checks skipped outside git"))
    elif git_checks and repo is not None:
        relative = path.resolve().relative_to(repo)
        if relative.parts[:2] != ("docs", "maps") or not re.fullmatch(
            r"[a-z]+(?:-[a-z]+){1,3}", path.stem
        ):
            warn("path", "map should be docs/maps/<two-to-four-lowercase-words>.md")
        log_path = subprocess.run(
            ["git", "-C", str(repo), "log", "-1", "--format=%H", "--", str(relative)],
            capture_output=True,
            text=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain", "--", str(relative)],
            capture_output=True,
            text=True,
        ).stdout.strip()
        if not log_path:
            warn("drift", "map is untracked")
        elif dirty:
            warn("drift", "map has uncommitted changes")
        else:
            count = subprocess.run(
                ["git", "-C", str(repo), "rev-list", "--count", f"{log_path}..HEAD"],
                capture_output=True,
                text=True,
            ).stdout.strip()
            if count and int(count):
                warn(
                    "drift",
                    f"{count} commits since the map last changed; see git log --oneline {log_path}..HEAD",
                )
        for stage in stages:
            evidence = re.sub(r"`[^`]*@[0-9a-fA-F]{7,40}`", "", stage["evidence"])
            for commit in re.findall(
                r"`([0-9a-fA-F]{7,40}(?:\.\.\.?[0-9a-fA-F]{7,40})?)`", evidence
            ):
                for sha in (
                    commit.split("...")
                    if "..." in commit
                    else commit.split("..")
                    if ".." in commit
                    else [commit]
                ):
                    if subprocess.run(
                        ["git", "-C", str(repo), "cat-file", "-e", f"{sha}^{{commit}}"],
                        capture_output=True,
                    ).returncode:
                        error(
                            f"stage {stage['id']}",
                            f"commit {sha} not found; write other repos' commits as repo@sha",
                        )
            for value in re.findall(r"`([^`]+)`", stage["evidence"]):
                if value.startswith("http") or "@" in value or (":" in value.split("/")[0]):
                    continue
                if (
                    "/" in value
                    and " " not in value
                    and not value.startswith(("~", "/", "$"))
                    and not (repo / value).exists()
                ):
                    warn(f"stage {stage['id']}", f"repo-relative path does not exist: {value}")
                if (
                    value
                    and "/" not in value
                    and subprocess.run(
                        [
                            "git",
                            "-C",
                            str(repo),
                            "show-ref",
                            "--verify",
                            "--quiet",
                            f"refs/heads/{value}",
                        ]
                    ).returncode
                    == 0
                ):
                    continue
        agents = next(
            (repo / name for name in ("AGENTS.md", "CLAUDE.md") if (repo / name).is_file()), None
        )
        if list((repo / "docs/maps").glob("*.md")) and (
            agents is None or "docs/maps" not in agents.read_text(encoding="utf-8")
        ):
            warn("AGENTS.md", "repo with maps should mention docs/maps in AGENTS.md or CLAUDE.md")
    if any(
        not re.match(r"\d{4}-\d{2}-\d{2}(?:\s|$)", line)
        for line in re.findall(r"^-\s+(.*)$", sections.get("Log", ""), re.M)
    ):
        warn("Log", "Log bullet without a leading YYYY-MM-DD date")
    if not any(
        line.strip() and line.strip() != "- None" for line in sections.get("Log", "").splitlines()
    ) and any(state(stage) != "todo" for stage in stages):
        warn("Log", "Log is empty after a stage left Todo")
    if (
        status == "active"
        and stages
        and all(state(stage) in {"done", "dropped"} for stage in stages)
    ):
        warn("status", "ready to finish: references/finish.md")
    frontier = active + ready_stages + waiting
    return findings, {
        "data": data,
        "stages": stages,
        "active": active,
        "ready": ready_stages,
        "waiting": waiting,
        "frontier": frontier,
    }


def print_findings(findings):
    for kind, area, message in findings:
        print(f"{kind}: {message}" if kind == "note" else f"{kind} {area}: {message}")


def audit(path):
    findings, state_data = check(path)
    if state_data:
        print_findings(findings)
        frontier = state_data["frontier"]
        print(
            "next: "
            + (
                "; ".join(f"{s['id']} {s['title']}" for s in frontier)
                if frontier
                else "none (all stages done or dropped)"
            )
        )
    errors = sum(kind == "ERROR" for kind, _, _ in findings)
    warnings = sum(kind == "WARN" for kind, _, _ in findings)
    print(f"audit: {errors} errors, {warnings} warnings")
    return 2 if state_data is None else 1 if errors else 0


def claim(path, stage_id):
    findings, state_data = check(path, git_checks=False)
    errors = [item for item in findings if item[0] == "ERROR"]
    if errors:
        print_findings(errors)
        print("fix these errors with audit first")
        return 1
    stages = state_data["stages"]
    stage = next((item for item in stages if item["id"] == stage_id), None)
    if stage is None:
        print(f"unknown stage id: {stage_id}")
        return 1
    current = state(stage)
    original = path.read_bytes()
    git = shutil.which("git")
    repo = (
        subprocess.run(
            [git, "-C", str(path.resolve().parent), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
        )
        if git
        else None
    )
    root = repo.stdout.strip() if repo and repo.returncode == 0 else None
    relative = str(path.resolve().relative_to(root)) if root else None
    if root and relative and git:
        dirty = subprocess.run(
            [git, "-C", root, "status", "--porcelain", "--", relative],
            capture_output=True,
            text=True,
        )
        if dirty.stdout.strip():
            print(
                "map has uncommitted changes (another session may be editing it): wait for its commit, then claim again"
            )
            return 1
    if current in {"done", "dropped"}:
        print(f"stage {stage_id} is {current}; cannot claim it")
        return 1
    if current == "active":
        print(
            f"stage {stage_id} is already Active; continue from its Where it stopped. If another session is working it, choose another stage."
        )
        return 0
    by_id = {item["id"]: item for item in stages}
    unmet = [dep for dep in dependencies(stage) if dep not in by_id or state(by_id[dep]) != "done"]
    if current == "todo" and unmet:
        print(f"stage {stage_id} waits on: {', '.join(unmet)}")
        return 1
    data = state_data["data"]
    if not data["briefs"].get(stage_id):
        print(f"write the brief for stage {stage_id} first")
        return 1
    text = original.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    row_index = next(
        i
        for i, line in enumerate(lines)
        if line.lstrip().startswith("|")
        and len(split_cells(line)) == 5
        and split_cells(line)[0] == stage_id
    )
    cells = split_cells(lines[row_index])
    cells[3] = "Active"
    lines[row_index] = rebuild_row(cells, newline, lines[row_index].endswith(("\n", "\r")))
    text = "".join(lines)
    now = datetime.datetime.now().astimezone()
    claim_time = now.strftime("%Y-%m-%d %H:%M")
    brief_match = re.search(rf"(?m)^### Stage\s+{re.escape(stage_id)}:.*$", text)
    if brief_match is None:
        path.write_bytes(original)
        print(f"write the brief for stage {stage_id} first")
        return 1
    brief_end = re.search(r"(?m)^### |^## ", text[brief_match.end() :])
    end = brief_match.end() + brief_end.start() if brief_end else len(text)
    brief = text[brief_match.start() : end]
    if "**Where it stopped:**" not in brief:
        bullets = list(re.finditer(r"(?m)^- .*?(?:\r?\n|$)", brief))
        pos = brief_match.start() + (bullets[-1].end() if bullets else len(brief))
        text = (
            text[:pos]
            + f"- **Where it stopped:** nothing yet (started {claim_time}){newline}"
            + text[pos:]
        )
    log_header = re.search(r"(?m)^## Log\s*$", text)
    if log_header is None:
        path.write_bytes(original)
        print("map has no Log section")
        return 1
    log_end = re.search(r"(?m)^## ", text[log_header.end() :])
    log_stop = log_header.end() + log_end.start() if log_end else len(text)
    log = text[log_header.end() : log_stop]
    bullets = list(re.finditer(r"(?m)^- .*?(?:\r?\n|$)", log))
    pos = log_header.end() + (bullets[-1].end() if bullets else len(log))
    text = text[:pos] + f"- {claim_time} Stage {stage_id} claimed.{newline}" + text[pos:]
    path.write_bytes(
        (b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b"") + text.encode("utf-8")
    )
    findings, checked = check(path, git_checks=False)
    if any(item[0] == "ERROR" for item in findings):
        path.write_bytes(original)
        print_findings(findings)
        return 1
    if git is None:
        print(f"claimed stage {stage_id}: Active")
        print("note: not in git; map edited but not committed")
        return 0
    if root and relative:
        subprocess.run([git, "-C", root, "add", "--", relative], check=True)
        result = subprocess.run(
            [
                git,
                "-C",
                root,
                "commit",
                "-q",
                "-m",
                f"map: {path.stem} stage {stage_id} active",
                "--",
                relative,
            ],
            text=True,
            capture_output=True,
        )
        if result.returncode:
            print(result.stderr.strip() or result.stdout.strip())
            print(
                f"stage {stage_id} is claimed but NOT committed; commit the map before doing stage work"
            )
            return 1
        sha = subprocess.check_output(
            [git, "-C", root, "rev-parse", "--short", "HEAD"], text=True
        ).strip()
        print(f"claimed stage {stage_id}: Active (commit {sha})")
    else:
        print(f"claimed stage {stage_id}: Active")
        print("note: not in git; map edited but not committed")
    return 0


def list_maps(root, all_maps):
    if not root.exists():
        print(f"no such path: {root}")
        return
    files = [root] if root.is_file() else sorted((root / "docs/maps").glob("*.md"))
    if not files:
        print(f"no maps under {root}/docs/maps")
        return
    hidden = 0
    for path in files:
        findings, state_data = check(path, git_checks=False)
        if state_data is None:
            print(f"{path}: unreadable; run audit")
            continue
        data, stages = state_data["data"], state_data["stages"]
        if not all_maps and data["status"] in {"done", "dropped"}:
            hidden += 1
            continue
        done = sum(state(stage) == "done" for stage in stages)
        questions = sum(
            line.strip().startswith("- ") and line.strip() != "- None"
            for line in data["sections"].get("Open questions", "").splitlines()
        )
        errors = sum(kind == "ERROR" for kind, _, _ in findings)
        print(
            f"{path}: {data['title']} [{data['status']}] {done}/{len(stages)} stages; open questions: {questions}"
            + (f" ({errors} errors: run audit)" if errors else "")
        )
        for name, group in (
            ("Active", state_data["active"]),
            ("ready", state_data["ready"]),
            ("Waiting", state_data["waiting"]),
        ):
            print(f"  {name}:")
            for stage in group:
                stage_note = note(stage) if name == "Waiting" else ""
                print(
                    f"    {stage['id']} {stage['title']}"
                    + (f" ({stage_note})" if stage_note else "")
                )
    if hidden:
        print(f"{hidden} finished or dropped maps hidden (use --all)")


def main():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="command", required=True)
    status_parser = subs.add_parser("status")
    status_parser.add_argument("--all", action="store_true")
    status_parser.add_argument("paths", nargs="*")
    audit_parser = subs.add_parser("audit")
    audit_parser.add_argument("map")
    claim_parser = subs.add_parser("claim")
    claim_parser.add_argument("map")
    claim_parser.add_argument("stage")
    args = parser.parse_args()
    if args.command == "audit":
        return audit(pathlib.Path(args.map))
    if args.command == "claim":
        return claim(pathlib.Path(args.map), args.stage)
    roots = [pathlib.Path(item) for item in args.paths] or [pathlib.Path.cwd()]
    for root in roots:
        list_maps(root, args.all)
    return 0


if __name__ == "__main__":
    sys.exit(main())
