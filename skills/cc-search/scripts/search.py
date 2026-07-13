#!/usr/bin/env python3
"""Full-text search across past Claude Code sessions and plan files.

Claude Code stores conversations as JSONL under ``~/.claude/projects`` and
saved plans as markdown under ``~/.claude/plans``. The built-in ``/resume``
only searches conversation titles, so this script searches the actual message
text (and plan bodies) and prints matching snippets with a ready-to-run
``claude --resume <id>`` command for each session.

The script is read-only and depends only on the standard library.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

PROJECTS_DIR = Path.home() / ".claude" / "projects"
PLANS_DIR = Path.home() / ".claude" / "plans"

# Content block types worth searching by default. ``thinking`` and ``image``
# are excluded as noise; tool output is gated behind ``--include-tools``.
DEFAULT_BLOCK_TYPES = frozenset({"text"})
TOOL_BLOCK_TYPES = frozenset({"tool_result"})

ROLE_ICONS = {"user": "\N{BUST IN SILHOUETTE}", "assistant": "\N{ROBOT FACE}"}

# ANSI bold, only emitted when writing to a terminal.
_BOLD = "\033[1m"
_RESET = "\033[0m"


@dataclass
class Snippet:
    """A single matching excerpt with a role hint for display."""

    role: str
    text: str


@dataclass
class SessionHit:
    """Aggregated matches for one session JSONL file."""

    session_id: str
    project: str  # Real working directory path (from the ``cwd`` field).
    title: str
    timestamp: str
    snippets: list[Snippet] = field(default_factory=list)


@dataclass
class PlanHit:
    """Aggregated matches for one plan markdown file."""

    path: Path
    title: str
    mtime: float
    snippets: list[Snippet] = field(default_factory=list)


def project_matches(dirname: str, needle: str) -> bool:
    """Case-insensitively test a project filter against an encoded dir name.

    Claude Code encodes the working directory by replacing path separators
    with dashes (e.g. ``-Users-me-work-my-proj``). Because directory names can
    themselves contain dashes, we cannot losslessly decode back to a path — so
    we match against the encoded name, normalizing any slashes in the user's
    filter to dashes first (``personal/my-proj`` -> ``personal-my-proj``).
    """
    return needle.replace("/", "-").lower() in dirname.lower()


def project_label(cwd: str) -> str:
    """Short, human-friendly project name (the last path segment of ``cwd``)."""
    tail = cwd.rstrip("/").rsplit("/", 1)[-1]
    return tail or cwd


def compile_pattern(query: str, use_regex: bool) -> re.Pattern:
    """Compile the query into a case-insensitive pattern.

    Plain queries are escaped so regex metacharacters are treated literally.
    """
    source = query if use_regex else re.escape(query)
    return re.compile(source, re.IGNORECASE)


def make_snippet(text: str, match: re.Match, context: int, color: bool) -> str:
    """Build a one-line excerpt around ``match`` with surrounding context."""
    start = max(match.start() - context, 0)
    end = min(match.end() + context, len(text))
    before = text[start:match.start()]
    hit = text[match.start():match.end()]
    after = text[match.end():end]
    if color:
        hit = f"{_BOLD}{hit}{_RESET}"
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    excerpt = f"{prefix}{before}{hit}{after}{suffix}"
    return " ".join(excerpt.split())


def extract_blocks(content, include_tools: bool) -> list[tuple[Optional[str], str]]:
    """Normalize a message ``content`` field into searchable text blocks.

    ``content`` may be a plain string or a list of typed blocks. Returns a
    list of ``(block_type, text)`` tuples for the block types we search.
    """
    wanted = DEFAULT_BLOCK_TYPES | (TOOL_BLOCK_TYPES if include_tools else frozenset())
    if isinstance(content, str):
        return [("text", content)]
    if not isinstance(content, list):
        return []
    blocks: list[tuple[Optional[str], str]] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        btype = block.get("type")
        if btype not in wanted:
            continue
        if btype == "tool_result":
            text = _tool_result_text(block.get("content"))
        else:
            text = block.get("text", "")
        if text:
            blocks.append((btype, text))
    return blocks


def _tool_result_text(content) -> str:
    """Flatten a ``tool_result`` block's content into a single string."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        ]
        return "\n".join(p for p in parts if p)
    return ""


def search_session(
    path: Path,
    pattern: re.Pattern,
    matches_per: int,
    context: int,
    role_filter: str,
    include_tools: bool,
    color: bool,
) -> Optional[SessionHit]:
    """Scan one session file and return a hit if any message text matches."""
    session_id = path.stem
    project = path.parent.name.replace("-", "/")
    title = ""
    latest_ts = ""
    snippets: list[Snippet] = []
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                cwd = record.get("cwd")
                if cwd:
                    project = cwd
                slug = record.get("slug")
                if slug:
                    title = slug
                message = record.get("message")
                if not isinstance(message, dict):
                    continue
                role = message.get("role", "")
                if role_filter != "any" and role != role_filter:
                    continue
                if len(snippets) >= matches_per:
                    continue
                for _btype, text in extract_blocks(message.get("content"), include_tools):
                    match = pattern.search(text)
                    if match is None:
                        continue
                    snippets.append(Snippet(role, make_snippet(text, match, context, color)))
                    ts = record.get("timestamp", "")
                    if ts > latest_ts:
                        latest_ts = ts
                    if len(snippets) >= matches_per:
                        break
    except OSError:
        return None
    if not snippets:
        return None
    return SessionHit(session_id, project, title or session_id, latest_ts, snippets)


def search_plan(
    path: Path,
    pattern: re.Pattern,
    matches_per: int,
    context: int,
    color: bool,
) -> Optional[PlanHit]:
    """Scan one plan markdown file and return a hit if its body matches."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    snippets: list[Snippet] = []
    title = path.stem
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    for match in pattern.finditer(text):
        snippets.append(Snippet("plan", make_snippet(text, match, context, color)))
        if len(snippets) >= matches_per:
            break
    if not snippets:
        return None
    return PlanHit(path, title, path.stat().st_mtime, snippets)


def iter_session_files(project_filter: str) -> list[Path]:
    """Return session JSONL paths, newest first, honoring the project filter."""
    if not PROJECTS_DIR.is_dir():
        return []
    files: list[Path] = []
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        if project_filter and not project_matches(project_dir.name, project_filter):
            continue
        files.extend(project_dir.glob("*.jsonl"))
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def iter_plan_files() -> list[Path]:
    """Return plan markdown paths, newest first."""
    if not PLANS_DIR.is_dir():
        return []
    files = sorted(
        PLANS_DIR.glob("*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files


def format_ts(raw: str) -> str:
    """Format an ISO timestamp as ``YYYY-MM-DD HH:MM``; pass through on error."""
    if not raw:
        return "?"
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return raw
    return parsed.strftime("%Y-%m-%d %H:%M")


def format_mtime(mtime: float) -> str:
    """Format a filesystem mtime as ``YYYY-MM-DD HH:MM``."""
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")


def print_sessions(hits: list[SessionHit]) -> None:
    """Render session hits grouped under a header."""
    print("SESSIONS " + "─" * 50)
    for hit in hits:
        title = hit.title if hit.title != hit.session_id else "(untitled)"
        print(f'[{project_label(hit.project)}]  {format_ts(hit.timestamp)}  "{title}"')
        for snippet in hit.snippets:
            icon = ROLE_ICONS.get(snippet.role, "\N{BLACK SMALL SQUARE}")
            print(f"  {icon} {snippet.text}")
        print(f"  \N{BLACK RIGHT-POINTING TRIANGLE} claude --resume {hit.session_id}")
        print()


def print_plans(hits: list[PlanHit]) -> None:
    """Render plan hits grouped under a header."""
    print("PLANS " + "─" * 53)
    home = str(Path.home())
    for hit in hits:
        print(f"[plan]  {format_mtime(hit.mtime)}  {hit.title}")
        for snippet in hit.snippets:
            print(f"  {snippet.text}")
        display = str(hit.path).replace(home, "~", 1)
        print(f"  \N{PAGE FACING UP} {display}")
        print()


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Define and parse the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Full-text search across Claude Code sessions and plans."
    )
    parser.add_argument("query", help="text or regex to search for")
    parser.add_argument(
        "--type",
        choices=("sessions", "plans", "all"),
        default="all",
        help="what to search (default: all)",
    )
    parser.add_argument(
        "--project",
        default="",
        help="only sessions whose project path contains this substring",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="max sessions/plans to report (default: 20)",
    )
    parser.add_argument(
        "--matches-per",
        type=int,
        default=3,
        help="max snippets per session/plan (default: 3)",
    )
    parser.add_argument(
        "--context",
        type=int,
        default=100,
        help="chars of context around each match (default: 100)",
    )
    parser.add_argument(
        "--regex",
        action="store_true",
        help="treat query as a regular expression",
    )
    parser.add_argument(
        "--role",
        choices=("user", "assistant", "any"),
        default="any",
        help="restrict session matches by speaker role (default: any)",
    )
    parser.add_argument(
        "--include-tools",
        action="store_true",
        help="also search tool_result output blocks",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point. Returns a process exit code."""
    args = parse_args(argv)
    try:
        pattern = compile_pattern(args.query, args.regex)
    except re.error as exc:
        print(f"Invalid regex: {exc}", file=sys.stderr)
        return 2

    color = sys.stdout.isatty()
    session_hits: list[SessionHit] = []
    plan_hits: list[PlanHit] = []

    if args.type in ("sessions", "all"):
        for path in iter_session_files(args.project):
            if len(session_hits) >= args.limit:
                break
            hit = search_session(
                path,
                pattern,
                args.matches_per,
                args.context,
                args.role,
                args.include_tools,
                color,
            )
            if hit is not None:
                session_hits.append(hit)

    if args.type in ("plans", "all"):
        for path in iter_plan_files():
            if len(plan_hits) >= args.limit:
                break
            hit = search_plan(path, pattern, args.matches_per, args.context, color)
            if hit is not None:
                plan_hits.append(hit)

    if not session_hits and not plan_hits:
        print("No matches. Try a broader query or --type all.")
        return 0

    if session_hits:
        print_sessions(session_hits)
    if plan_hits:
        print_plans(plan_hits)
    return 0


if __name__ == "__main__":
    sys.exit(main())
