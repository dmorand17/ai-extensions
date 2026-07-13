---
name: cc-search
description: >
  Full-text search across past Claude Code sessions and plan files. Use when
  the user wants to find, resume, or recall a previous conversation or plan by
  its content (not just its title) — e.g. "find the session where we discussed
  X", "search my past conversations for Y", "which plan covered Z", "resume the
  chat about...". Searches message text in ~/.claude/projects and plan markdown
  in ~/.claude/plans, unlike the built-in /resume which only matches titles.
argument-hint: "search term (and optional --project / --type / --limit)"
---

Search the user's local Claude Code history for a term and present the matches.

## Run the search

```bash
python3 ~/.claude/skills/cc-search/scripts/search.py "<query>" [flags]
```

Wrap the query in quotes. The script is read-only and stdlib-only (no install
needed).

### Flags

| Flag | Default | Meaning |
|------|---------|---------|
| `--type {sessions,plans,all}` | `all` | Which store to search |
| `--project SUBSTR` | (none) | Only sessions whose project path contains SUBSTR |
| `--limit N` | `20` | Max sessions/plans to report |
| `--matches-per N` | `3` | Max snippets per session/plan |
| `--context N` | `100` | Chars of context around each match |
| `--regex` | off | Treat the query as a regular expression |
| `--role {user,assistant,any}` | `any` | Restrict session matches by speaker |
| `--include-tools` | off | Also search tool output (`tool_result`) blocks |

By default the query is a case-insensitive **substring** match over `text`
blocks (user/assistant messages). `thinking`, `image`, and tool blocks are
skipped unless `--include-tools` is passed.

## Present the results

The script prints two groups (SESSIONS, then PLANS), newest first. For each hit:

- **Sessions:** project name, timestamp, title/slug, matching snippet(s), and a
  `claude --resume <id>` command.
- **Plans:** timestamp, title, matching snippet(s), and the file path.

Relay the most relevant hits to the user. For a session they want to continue,
give them the exact `claude --resume <id>` command. For a plan, give the path.

If the script prints "No matches", tell the user and suggest broadening the term,
dropping `--project`, or using `--type all`.
