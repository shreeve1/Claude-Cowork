"""Memory note link graph: outgoing links, and backlinks computed by reversing it on demand."""
import re
from pathlib import Path, PurePosixPath

EXCLUDE_NAMES = {"README.md", "TEMPLATES.md"}
EXCLUDE_PARTS = {"raw", "candidates"}
MARKDOWN_LINK = re.compile(r"\]\((memory/[^)\s#]+\.md)(?:#[^)]*)?\)")
TICKED_PATH = re.compile(r"`(memory/[^`\s]+\.md)`")
UNLINKABLE = re.compile(r"[<>*]|(^|/)\.\.(/|$)")


def _sources(memory_dir):
    return [p for p in memory_dir.rglob("*.md")
            if p.name not in EXCLUDE_NAMES and not EXCLUDE_PARTS & set(p.parts)]


def _rel(p, memory_dir):
    return "memory/" + p.relative_to(memory_dir).as_posix()


def is_generated(path):
    """Indexes and hubs list every note, so they say nothing about whether a note is connected."""
    p = PurePosixPath(path)
    return p.name == "index.md" or "_hubs" in p.parts


def build(memory_dir):
    """Outgoing links per source page, as memory/<rel> paths; broken targets included."""
    graph = {}
    for p in _sources(memory_dir):
        # errors="replace": bloat already flags non-UTF8; links must not crash on it
        text = p.read_text(encoding="utf-8", errors="replace")
        found = set(MARKDOWN_LINK.findall(text)) | set(TICKED_PATH.findall(text))
        found = {t.split("#", 1)[0] for t in found if not UNLINKABLE.search(t)}
        found.discard(_rel(p, memory_dir))
        graph[_rel(p, memory_dir)] = frozenset(found)
    return graph


def notes(graph):
    return sorted(src for src in graph if not is_generated(src))


def broken(graph, memory_dir):
    out = []
    for src, targets in graph.items():
        for t in sorted(targets):
            if not (memory_dir / Path(t).relative_to("memory")).exists():
                out.append((src, t))
    return sorted(out)


def backlinks(graph, path):
    return sorted(src for src, targets in graph.items() if path in targets)


def no_outgoing(graph):
    return [src for src in notes(graph) if not graph[src]]


def no_inbound(graph):
    linked = set().union(*(graph[src] for src in notes(graph)))
    return [src for src in notes(graph) if src not in linked]
