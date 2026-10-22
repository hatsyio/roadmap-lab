"""Validate roadmap.toml and keep the README checklist table in sync with it.

Usage:
    python scripts/roadmap.py check    # validate + fail if README.md is stale
    python scripts/roadmap.py render   # validate + rewrite the README table
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Any

ROADMAP_FILE = "roadmap.toml"
README_FILE = "README.md"
START_MARKER = "<!-- roadmap:start -->"
END_MARKER = "<!-- roadmap:end -->"
ROADMAP_URL_PREFIX = "https://roadmap.sh/"
NODE_KEYS = frozenset({"roadmap", "node", "title", "status", "evidence"})


class Status(StrEnum):
    PENDING = "pending"
    EVIDENCED = "evidenced"


@dataclass(frozen=True)
class Node:
    roadmap: str
    node: str
    title: str
    status: Status
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class Roadmap:
    urls: dict[str, str]
    nodes: tuple[Node, ...]


class RoadmapError(Exception):
    def __init__(self, problems: list[str]) -> None:
        super().__init__("\n".join(problems))
        self.problems = problems


def load(root: Path) -> Roadmap:
    path = root / ROADMAP_FILE
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise RoadmapError([f"invalid TOML: {exc}"]) from exc
    return _parse(raw, root)


def _parse(raw: dict[str, Any], root: Path) -> Roadmap:
    problems: list[str] = []
    urls = _parse_urls(raw.get("roadmaps"), problems)
    nodes: list[Node] = []
    seen: set[tuple[str, str]] = set()

    raw_nodes = raw.get("nodes")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        problems.append("[[nodes]] must contain at least one node")
        raw_nodes = []

    for index, item in enumerate(raw_nodes, start=1):
        node = _parse_node(item, f"node #{index}", urls, root, problems)
        if node is None:
            continue
        key = (node.roadmap, node.node)
        if key in seen:
            problems.append(f"node #{index}: duplicate node {node.roadmap}/{node.node}")
        seen.add(key)
        nodes.append(node)

    if problems:
        raise RoadmapError(problems)
    return Roadmap(urls=urls, nodes=tuple(nodes))


def _parse_urls(raw: object, problems: list[str]) -> dict[str, str]:
    if not isinstance(raw, dict) or not raw:
        problems.append("[roadmaps] must map each roadmap id to its roadmap.sh URL")
        return {}
    urls: dict[str, str] = {}
    for roadmap_id, url in raw.items():
        if not isinstance(url, str) or not url.startswith(ROADMAP_URL_PREFIX):
            problems.append(f"[roadmaps] {roadmap_id}: URL must start with {ROADMAP_URL_PREFIX}")
            continue
        urls[roadmap_id] = url
    return urls


def _parse_node(
    item: object, where: str, urls: dict[str, str], root: Path, problems: list[str]
) -> Node | None:
    if not isinstance(item, dict):
        problems.append(f"{where}: must be a table")
        return None
    keys = set(item)
    if keys != NODE_KEYS:
        missing = sorted(NODE_KEYS - keys)
        unknown = sorted(keys - NODE_KEYS)
        problems.append(f"{where}: missing keys {missing}, unknown keys {unknown}")
        return None

    roadmap, slug, title = item["roadmap"], item["node"], item["title"]
    if not all(isinstance(value, str) and value for value in (roadmap, slug, title)):
        problems.append(f"{where}: roadmap, node and title must be non-empty strings")
        return None
    where = f"{where} ({roadmap}/{slug})"

    if roadmap not in urls:
        problems.append(f"{where}: roadmap '{roadmap}' is not declared in [roadmaps]")

    try:
        status = Status(item["status"])
    except ValueError:
        allowed = ", ".join(s.value for s in Status)
        problems.append(f"{where}: status must be one of: {allowed}")
        return None

    evidence = item["evidence"]
    if not isinstance(evidence, list) or not all(isinstance(p, str) for p in evidence):
        problems.append(f"{where}: evidence must be a list of paths")
        return None

    if status is Status.EVIDENCED and not evidence:
        problems.append(f"{where}: an evidenced node needs at least one evidence path")
    if status is Status.PENDING and evidence:
        problems.append(f'{where}: a pending node lists evidence; set status = "evidenced"')
    for entry in evidence:
        problem = _check_evidence_path(entry, root)
        if problem:
            problems.append(f"{where}: evidence '{entry}' {problem}")

    return Node(roadmap, slug, title, status, tuple(evidence))


def _check_evidence_path(entry: str, root: Path) -> str | None:
    posix = PurePosixPath(entry)
    if posix.is_absolute() or ".." in posix.parts:
        return "must be a relative path inside the repo"
    if not (root / posix).exists():
        return "does not exist"
    return None


def render_table(roadmap: Roadmap) -> str:
    done = sum(1 for n in roadmap.nodes if n.status is Status.EVIDENCED)
    lines = [
        f"Evidenced: **{done} / {len(roadmap.nodes)}**",
        "",
        "| Roadmap | Node | Status | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for node in roadmap.nodes:
        evidence = "<br>".join(f"[`{p}`]({p})" for p in node.evidence) or "-"
        lines.append(
            f"| [{node.roadmap}]({roadmap.urls[node.roadmap]}) "
            f"| {node.title} (`{node.node}`) | {node.status.value} | {evidence} |"
        )
    return "\n".join(lines)


def splice(readme: str, table: str) -> str:
    start = readme.find(START_MARKER)
    end = readme.find(END_MARKER)
    if start == -1 or end == -1 or end < start:
        raise RoadmapError([f"{README_FILE} must contain {START_MARKER} followed by {END_MARKER}"])
    head = readme[: start + len(START_MARKER)]
    return f"{head}\n{table}\n{readme[end:]}"


def run(command: str, root: Path) -> int:
    try:
        table = render_table(load(root))
        readme_path = root / README_FILE
        current = readme_path.read_text(encoding="utf-8")
        expected = splice(current, table)
    except RoadmapError as exc:
        for problem in exc.problems:
            print(f"{ROADMAP_FILE}: {problem}", file=sys.stderr)
        return 1

    if current == expected:
        return 0
    if command == "check":
        print(
            f"{README_FILE} is out of date with {ROADMAP_FILE}. "
            "Run `make readme` and commit the result.",
            file=sys.stderr,
        )
        return 1
    readme_path.write_text(expected, encoding="utf-8")
    print(f"{README_FILE} updated.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("command", choices=["check", "render"])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    return run(args.command, args.root)


if __name__ == "__main__":
    sys.exit(main())
