---
name: project-memory
description: >
  Set up and maintain a structured project memory system in
  docs/project_notes/ that tracks bugs with solutions, architectural
  decisions, key project facts, and work history. Use when user asks to
  "set up project memory", "initialize memory system", "track our
  decisions", "log a bug fix", "record an ADR", "update key facts", or
  whenever a problem feels familiar ("didn't we solve this before?").
---

## When to use

- Initializing memory infrastructure on a new or existing project
- Logging a bug + solution after resolving an issue
- Recording an architectural decision (ADR)
- Updating a project fact (port, URL, credential location, naming convention)
- Logging work against a ticket or issue
- Before proposing an architectural change — check `decisions.md` first
- When a problem feels familiar — search `bugs.md` first

## File layout

Files live in `docs/project_notes/`. Naming as plain engineering docs (not
"memory") so they look like ordinary project notes.

```
docs/
└── project_notes/
    ├── bugs.md         # Bug log with solutions
    ├── decisions.md    # Architectural Decision Records
    ├── key_facts.md    # Project configuration and constants
    └── issues.md       # Work log with ticket references
```

## Initial setup

Run once per project. Creates the directory, the four files (with the
templates from this skill), and adds a memory-aware section to `CLAUDE.md`.

1. `mkdir -p docs/project_notes`
2. Create each file using the templates in *File templates* below.
3. Add the *CLAUDE.md addition* (below) to the project's `CLAUDE.md`. If
   `CLAUDE.md` doesn't exist, create it with that section.

## File templates

Each file starts with a short header explaining what it is, followed by
entries newest-first. Use ISO dates (YYYY-MM-DD).

### bugs.md

```markdown
# Bugs

Log of resolved bugs with their root cause and fix. Search this before
investigating a familiar-sounding issue.

---

## YYYY-MM-DD — <short symptom>

**Symptom:** what the user/system observed
**Root cause:** what was actually wrong
**Fix:** what was changed (file paths, brief diff if useful)
**References:** ticket / PR / commit links
```

**Example entry:**

```markdown
## 2026-04-12 — Login redirects loop on Safari

**Symptom:** Safari users hit /login → /dashboard → /login indefinitely.
**Root cause:** Session cookie was set with `SameSite=None` but without
`Secure`, which Safari silently drops.
**Fix:** Added `Secure: true` to the cookie config in
`src/auth/session.ts:42`. Verified on Safari 17.
**References:** PR #482, ticket AUTH-119
```

### decisions.md

Lightweight ADRs (Nygard-style). One entry per architectural decision.

```markdown
# Decisions

Architectural decisions with the context and trade-offs that drove them.
Read this before proposing structural changes.

---

## ADR-NNN: <title>

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Superseded by ADR-MMM | Deprecated

**Context:** the situation forcing a decision — constraints, prior state.

**Decision:** the choice we made, stated clearly.

**Consequences:** what becomes easier, what becomes harder, what's now
locked in.
```

**Example entry:**

```markdown
## ADR-007: Use Postgres for the write model

**Date:** 2026-03-04
**Status:** Accepted

**Context:** The order service needs strong consistency for inventory
reservation. The team already operates Postgres for billing; introducing
DynamoDB would add a new operational surface.

**Decision:** Use Postgres (RDS) as the write store. Reads served from a
read-model projection in DynamoDB.

**Consequences:** Write path stays simple with row-level locks. Read scale
handled separately via projection. Cross-aggregate transactions are
possible but discouraged — they couple bounded contexts.
```

ADR numbering is monotonic — never reuse a number, even if an ADR is
superseded.

### key_facts.md

Stable project facts the agent shouldn't have to rediscover. Group by
category. Prefer documented facts over assumptions.

```markdown
# Key Facts

Stable project configuration and conventions. Check here before making
assumptions about ports, URLs, credentials, or naming.

---

## Environments

- **prod:** <url> — account `<id>`, region `<region>`
- **staging:** <url> — account `<id>`, region `<region>`

## Ports

- API: 8080
- Worker metrics: 9090

## Credentials

- AWS profile names: `<list>`
- Secrets: stored in `<location>` (never inline)

## Conventions

- Python: 4-space indent, ruff for lint, pytest for tests
- Branch naming: `<type>/<ticket>-<slug>`
```

### issues.md

Work log keyed to tickets. One line per status change is fine — keep it
terse.

```markdown
# Issues

Work log with ticket references. Append-only; status changes get a new
line under the same ticket.

---

## TICKET-123 — <short title>

- 2026-05-10 — Started, spec at <link>
- 2026-05-12 — Blocked on <reason>
- 2026-05-14 — Unblocked, PR #<n>
- 2026-05-16 — Merged, closing
```

## CLAUDE.md addition

Append (or merge) this section into the project's `CLAUDE.md`:

```markdown
## Project Memory System

Memory lives in `docs/project_notes/`. Consult it during the workflows
below.

### Memory-aware protocols

**Before proposing architectural changes:**
- Read `docs/project_notes/decisions.md`. Don't reopen settled trade-offs
  silently — if you disagree with an ADR, surface it.

**When encountering errors or bugs:**
- Search `docs/project_notes/bugs.md` for the symptom. Reuse the
  documented fix if it matches.
- After resolving a new bug, append an entry to `bugs.md`.

**When looking up project configuration:**
- Check `docs/project_notes/key_facts.md` for ports, URLs, credentials,
  conventions. Prefer documented facts over assumptions.

**When working on a ticket:**
- Append status changes to `docs/project_notes/issues.md` under the
  ticket's heading.
```

## Workflows

### Log a bug fix

After resolving a bug:

1. Open `docs/project_notes/bugs.md`.
2. Insert a new entry at the top (under the file header), using the
   *bugs.md* template above.
3. Fill Symptom, Root cause, Fix, References. Keep each field to a few
   sentences — long debugging narratives belong in the PR description.
4. Stage and commit alongside the fix so memory and code stay in sync.

### Record an ADR

When a decision meets all three criteria from the user's standards
(hard to reverse, surprising without context, real trade-off):

1. Open `docs/project_notes/decisions.md`.
2. Find the highest existing `ADR-NNN`; new entry is `ADR-(N+1)`.
3. Append using the *decisions.md* template. Status starts as `Proposed`
   if it's still under discussion, `Accepted` once committed.
4. If the decision overrides an earlier ADR, update the older entry's
   Status to `Superseded by ADR-NNN` (don't delete it — history matters).

### Update a key fact

When a port, URL, credential location, or convention changes:

1. Open `docs/project_notes/key_facts.md`.
2. Edit in place under the right category. Don't append a new section
   for a changed value — overwrite it.
3. If the category doesn't exist yet, add it under a new heading.

### Log work on a ticket

When starting, blocking, unblocking, or closing work on a ticket:

1. Open `docs/project_notes/issues.md`.
2. If the ticket has no heading, append `## TICKET-XXX — <title>` at the
   bottom.
3. Append a single line under that heading: `- YYYY-MM-DD — <event>`.

### Update memory

If an entry turns out to be wrong or outdated:

- **bugs.md / key_facts.md:** edit in place. These reflect current truth.
- **decisions.md:** never edit a past ADR's body. Add a new ADR that
  supersedes it, and mark the old one's Status accordingly.
- **issues.md:** append a correction line; don't rewrite history.
