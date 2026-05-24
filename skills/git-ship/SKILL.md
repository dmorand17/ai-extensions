---
name: git-ship
description: >
  Git workflow skill — drafts and executes Conventional Commits, and on
  request runs the full ship flow (create branch, commit, push, open PR).
  Use when the user asks to write, generate, format, or review a commit
  message, "commit" / "stage and commit", or to "ship", "push and open a
  PR", "create a branch and PR", or any combination of branch + commit +
  push + PR. Do NOT use for merges, rebases, reverts, or other history
  rewrites.
---

# git-ship

This skill has three modes. **Default to commit-only.** Only enter ship
mode when the user explicitly asks for branching, pushing, or PR creation.

| Request                                              | Mode        |
|------------------------------------------------------|-------------|
| "write a commit message", "review my msg", "format"  | Draft only  |
| "commit this", "stage and commit", "commit my work"  | Commit      |
| "ship", "push and open a PR", "branch + commit + PR" | Ship        |

If the request is ambiguous, draft the message and ask before staging,
pushing, or opening a PR.

---

## Conventional Commits format

```
<type>(<scope>): <subject>

<body>

<footer>
```

- Header (type, scope, subject) is mandatory; body and footer optional
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

---

## Commit mode workflow

When committing (not just drafting), run these steps in order. Stop if any
step surfaces something unexpected.

### 1. Review status

Run `git status` (no `-uall` flag — it can OOM on large repos). Surface
anything unexpected:

- Untracked files the user may not have intended to include
- Files that look like secrets (`.env`, `*credentials*`, `*.pem`, keys)
- Large binaries or build artifacts
- Changes outside the area the user was working in

If anything looks off, **confirm with the user before staging.** Do not
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

### Commit error handling

- **Pre-commit hook failure:** the commit didn't happen — fix the
  underlying issue, re-stage, and create a NEW commit. Do not `--amend`.

---

## Ship mode workflow

Full flow: branch (if needed) → commit → push → PR. Auto-progress through
branch creation and committing; **pause for confirmation before push and
before opening the PR** (these affect the remote and other people).

### 1. Determine the target branch

Run `git branch --show-current` and `git status -sb`.

- **Already on a feature branch** (not `main` / `master` / `develop`):
  keep it
- **On the default branch with staged or unstaged changes**: create a new
  branch and move the working changes onto it

For new branches, follow the prefixes from
`~/.claude/guidelines/git-guidelines.md`:

| Prefix      | Purpose             |
|-------------|---------------------|
| `feat/`     | New features        |
| `fix/`      | Bug fixes           |
| `chore/`    | Maintenance/tooling |
| `docs/`     | Docs-only           |
| `refactor/` | Refactors           |

Slug: short, kebab-case, derived from the change. Example:
`feat/jwt-auth-middleware`.

```bash
git switch -c feat/jwt-auth
```

### 2. Commit

Run the **Commit mode workflow** above (status review → message → stage →
commit). Don't pause; only stop if step 1 surfaces something unexpected
(secrets, scope drift, etc.).

### 3. Confirm before pushing

Show the user:

- Current branch name
- Commit subject(s) about to be pushed (`git log @{u}..HEAD --oneline`,
  or `git log --oneline -n 5` if there's no upstream yet)
- Target remote (`git remote -v` — typically `origin`)

Wait for explicit "yes / push it / go ahead" before continuing. If the
user declines, stop.

### 4. Push

For a brand-new branch, set the upstream:

```bash
git push -u origin <branch>
```

For subsequent pushes, plain `git push`.

#### Push errors

- **Non-fast-forward / rejected**: stop. Do not force-push. Surface the
  rejection to the user and let them decide.
- **Auth failure**: stop and surface. Do not retry with different creds.

### 5. Confirm before opening a PR

Draft the PR title and body, then show the user before creating. Wait for
explicit approval.

**Title:** the commit subject if there's one commit; otherwise a concise
summary of the branch's intent. ≤ 70 chars.

**Body template:**

```markdown
## Summary
- <bullet 1>
- <bullet 2>

## Test plan
- [ ] <test step>
- [ ] <test step>
```

Read **all** commits on the branch (`git log <base>..HEAD` — use the
repo's actual base branch, usually `main`) to write the summary, not just
the latest one.

### 6. Create the PR with `gh`

```bash
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
- ...

## Test plan
- [ ] ...
EOF
)"
```

If the repo isn't on GitHub or `gh` isn't installed, stop and tell the
user — don't fall back to `cr`, `glab`, or other tools without asking.

After creation, return the PR URL.

---

## Safety rules (inherited from `~/.claude/CLAUDE.md`)

- Never publish secrets — verify `.env` and credential-like files are not
  staged.
- Never `git add -A` / `git add .` blindly.
- Never skip hooks (`--no-verify`, `--no-gpg-sign`) without explicit user
  instruction.
- Never amend a published commit; create a new one.
- Never run destructive git commands (`reset --hard`, `clean -f`,
  `branch -D`, `push --force`) as part of this workflow.
- Never push directly to `main` / `master` — always via a feature branch
  + PR.
