---
name: git-commit
description: >
  Stage and commit using Conventional Commits — or just draft/review a commit
  message without executing. Use this skill when the user asks to write,
  generate, format, or review a commit message, or when they ask to "commit"
  / "stage and commit" their changes. Do NOT use for pushing to a remote,
  branches, PRs, merges, rebases, or other git operations.
---

## Two modes

This skill handles both message-only and commit-execution requests. Read
the user's intent before acting:

| Request                                              | Mode               |
|------------------------------------------------------|--------------------|
| "write a commit message", "review my msg", "format"  | Draft only         |
| "commit this", "stage and commit", "commit my work"  | Execute            |

If unclear, draft the message and ask before staging/committing.

**This skill never pushes.** If the user asks to push, stop and tell them
to run the push themselves — there is no skill for it.

## Conventional Commits format

```
<type>(<scope>): <subject>

<body>

<footer>
```

- Header (type, scope, subject) is mandatory; body and footer are optional
- Header ≤ 50 chars (72 hard limit); body wrapped at 72
- Blank line between header, body, and footer

### Types

| Type       | Purpose                                          |
|------------|--------------------------------------------------|
| `feat`     | New feature                                      |
| `fix`      | Bug fix                                          |
| `docs`     | Documentation-only changes                       |
| `style`    | Formatting (no content changes)                  |
| `refactor` | Restructuring without adding/removing behavior   |
| `test`     | Adding or updating tests                         |
| `chore`    | Build process or auxiliary tool changes          |
| `build`    | Build-related changes                            |
| `ci`       | CI-related changes                               |
| `perf`     | Performance improvements                         |
| `revert`   | Reverting changes                                |

### Guidelines

- Imperative mood: "add" not "added" or "adds"
- Lowercase subject, no trailing period
- Scope optional but recommended (e.g., folder name or topic area)
- Body explains *what* and *why*, not *how*
- Breaking changes: add `!` after type/scope
- Reference issues in footer: `Closes #123`
- Do NOT include `Co-Authored-By: Claude` unless the user has it in their
  global rules (`~/AGENTS.md` / `CLAUDE.md`)

### Example

Input: "added user auth with JWT tokens"
Output: `feat(auth): implement JWT-based authentication`

## Execute mode workflow

When committing (not just drafting), run these steps in order. Stop if
any step surfaces something unexpected.

### 1. Review status

Run `git status` (no `-uall` flag — it can OOM on large repos). Surface
anything unexpected:

- Untracked files the user may not have intended to include
- Files that look like secrets (`.env`, `*credentials*`, `*.pem`, keys)
- Large binaries or build artifacts
- Changes outside the area the user was working in

If anything looks off, **confirm with the user before staging**. Do not
auto-stage with `git add -A` or `git add .` — stage specific files by
name after the user has signed off on what's included.

### 2. Generate the commit message

Run `git diff --staged` (or `git diff` if nothing is staged) to read the
actual changes, then draft a message following the format above.

### 3. Stage and commit

Stage specific files, then commit via a HEREDOC to preserve formatting:

```bash
git add path/to/file1 path/to/file2
git commit -m "$(cat <<'EOF'
<type>(<scope>): <subject>

<body>
EOF
)"
```

After the commit, run `git status` to confirm.

## Error handling

- **Pre-commit hook failure:** the commit didn't happen — fix the
  underlying issue, re-stage, and create a NEW commit. Do not `--amend`.
- **Hook can't reach Docker / Colima** (signatures: `Cannot connect to
  the Docker daemon`, `colima ... no such file`, `unix socket ...
  connection refused`): stop and report verbatim. Do not run
  `colima start` / `open -a Docker` without explicit instruction. Do
  not retry with `--no-verify`.

## Safety rules (inherited from `~/AGENTS.md`)

- Never publish secrets — verify `.env` and credential-like files are
  not staged.
- Never `git add -A` / `git add .` blindly.
- Never skip hooks (`--no-verify`, `--no-gpg-sign`) without explicit
  user instruction.
- Never amend a published commit; create a new one.
- Never run destructive git commands (`reset --hard`, `clean -f`,
  `branch -D`) as part of this workflow.
