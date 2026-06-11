---
name: handoff
description: >
  Compact the current conversation into a handoff document for another
  agent to pick up. Use when user says "handoff", "compact this
  conversation", "pass to another agent", "wrap up the session", or is
  approaching context limits and wants to continue the work in a fresh
  session.
argument-hint: "What will the next session be used for?"
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work.

**Before writing, ask the user where to save it.** Propose 2–3 sensible locations based on the current context (e.g. project root, alongside a referenced plan/PRD, a dedicated `~/.claude/handoffs/` directory) and recommend one with a brief reason. Do not default to `mktemp` — temp files get cleaned up and are hard to find later. Only fall back to `mktemp -t handoff-XXXXXX.md` if the user explicitly declines to pick a location.

Once the user confirms a path, write the doc there. Use a descriptive filename (e.g. `HANDOFF-<topic>.md`) rather than a generic one.

Suggest the skills to be used, if any, by the next session.

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
