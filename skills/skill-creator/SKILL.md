---
name: skill-creator
description: Create new agent skills with proper structure, progressive disclosure, and bundled resources. Use when user wants to create, write, or build a new skill.
---

# Writing Skills

## Process

1. **Gather requirements** - ask user about:
   - What task/domain does the skill cover?
   - What specific use cases should it handle?
   - Does it need executable scripts or just instructions?
   - Any reference materials to include?

2. **Draft the skill** - create:
   - SKILL.md with concise instructions
   - Additional reference files if content exceeds 300 lines
   - Utility scripts if deterministic operations needed

3. **Review with user** - present draft and ask:
   - Does this cover your use cases?
   - Anything missing or unclear?
   - Should any section be more/less detailed?

## Skill Structure

```
skill-name/
├── SKILL.md           # Main instructions (required)
├── references/        # Detailed docs (loaded on demand)
├── examples/          # Usage examples (if needed)
├── assets/            # Templates, icons, fonts
└── scripts/           # Utility scripts (if needed)
    └── helper.py
```

## SKILL.md Template

```md
---
name: skill-name
description: Brief description of capability. Use when [specific triggers].
---

# Skill Name

## Quick start

[Minimal working example]

## Workflows

[Step-by-step processes with checklists for complex tasks]

## Advanced features

[Link to separate files: See [reference.md](references/reference.md)]
```

## Description Requirements

The description is **the only thing the agent sees** when deciding which skill to load. It's surfaced in the system prompt alongside all other installed skills.

**Goal**: Give the agent enough info to know:

1. What capability this skill provides
2. When/why to trigger it (specific keywords, contexts, file types)

**Format**:

- Combined `description` + `when_to_use` truncates at 1,536 chars — front-load the key use case
- Write in third person
- First sentence: what it does
- Second sentence: "Use when [specific triggers]"

**Good example**:

```
Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when user mentions PDFs, forms, or document extraction.
```

**Bad example**:

```
Helps with documents.
```

## Frontmatter Reference

All fields are optional. Only `description` is recommended.

| Field | Purpose |
|-------|---------|
| `name` | Display name (defaults to directory name). Lowercase, hyphens, max 64 chars. |
| `description` | What it does and when to use it. Claude uses this for auto-triggering. |
| `when_to_use` | Extra trigger phrases appended to `description`. Shares 1,536-char cap. |
| `argument-hint` | Hint shown during `/`-autocomplete (e.g., `[issue-number]`). |
| `arguments` | Named positional args for `$name` substitution (space-separated or YAML list). |
| `disable-model-invocation` | `true` = only user can invoke via `/name`. Use for side-effect skills (deploy, commit). |
| `user-invocable` | `false` = hidden from `/` menu. Use for background knowledge Claude consults automatically. |
| `allowed-tools` | Tools Claude can use without per-use approval while skill is active (space-separated or YAML list). |
| `context` | `fork` = run in isolated subagent. Skill body becomes the subagent's prompt. |
| `agent` | Subagent type when `context: fork` is set (`Explore`, `Plan`, `general-purpose`, or custom). |
| `paths` | Glob patterns that gate auto-activation (e.g., `src/**/*.ts`). |
| `model` | Per-skill model override. `inherit` keeps the active model. |
| `effort` | Per-skill effort level: `low`, `medium`, `high`, `xhigh`, `max`. |
| `hooks` | Hooks scoped to this skill's lifecycle. |
| `shell` | `bash` (default) or `powershell` for inline shell commands. |

### Invocation Control

| Frontmatter | User can invoke | Claude can invoke |
|-------------|:-:|:-:|
| (default) | Yes | Yes |
| `disable-model-invocation: true` | Yes | No |
| `user-invocable: false` | No | Yes |

Use `disable-model-invocation: true` for skills with side effects (deploy, commit, send). Use `user-invocable: false` for background knowledge that isn't a meaningful user action.

### String Substitutions

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments passed when invoking. Appended automatically if not present in content. |
| `$ARGUMENTS[N]` / `$N` | Positional arg by 0-based index (e.g., `$0`, `$1`). |
| `$name` | Named arg from `arguments` frontmatter, mapped by position. |
| `${CLAUDE_SKILL_DIR}` | Directory containing this SKILL.md. Use for script paths. |
| `${CLAUDE_SESSION_ID}` | Current session ID. |
| `${CLAUDE_EFFORT}` | Current effort level. |

**Example:**

```yaml
---
name: fix-issue
description: Fix a GitHub issue
arguments: [issue, branch]
disable-model-invocation: true
---

Fix GitHub issue #$issue on branch $branch.
```

Invoke: `/fix-issue 123 main`

### Dynamic Context Injection

Inline `` !`command` `` runs a shell command at parse time and substitutes the output. Claude only sees the result, not the command.

```yaml
---
name: pr-summary
description: Summarize the current pull request
allowed-tools: Bash(gh *)
---

## PR context
- Diff: !`gh pr diff`
- Files changed: !`gh pr diff --name-only`

Summarize the changes above.
```

For multi-line commands, use a fenced block opened with ` ```! `.

### Subagent Execution

`context: fork` runs the skill body as a prompt to an isolated subagent with no conversation history. Only use for skills with an explicit task — pure guidelines have nothing for the subagent to do.

```yaml
---
name: deep-research
description: Research a topic thoroughly across the codebase
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly. Find relevant files via Glob/Grep,
read and analyze them, and return a summary with file references.
```

## Best Practices

### Ground Skills in Real Expertise

Weak skills come from asking an LLM to draft one with no project context. Effective skills come from:

- **Extracting from a hands-on task** — complete a real task, then capture the reusable pattern
- **Synthesizing from existing artifacts** — runbooks, API specs, incident reports, code review comments

### Spend Context Wisely

The context window is shared. Only add what the agent doesn't already know. Challenge each piece: "Would the agent get this wrong without this?"

- Keep SKILL.md under 300 lines
- Reference files clearly from SKILL.md with guidance on *when* to read them
- For large reference files (>300 lines), include a table of contents

### Calibrate Control

- **High freedom** (text instructions): multiple valid approaches, heuristic guidance
- **Medium freedom** (pseudocode/parameterized scripts): preferred pattern with variation
- **Low freedom** (specific scripts): fragile operations, consistency critical

Provide defaults, not menus. Pick one approach and offer an escape hatch.

### Favor Procedures Over Declarations

Teach *how to approach* a class of problems, not *what to produce* for one instance. The approach should generalize even when individual details are concrete.

### Useful Patterns

- **Gotchas section** — environment-specific facts that defy reasonable assumptions (highest-value content in many skills)
- **Validation loops** — do the work, run a validator, fix issues, repeat until passing
- **Plan-validate-execute** — for batch/destructive ops: build plan, validate against source of truth, then execute
- **Output templates** — concrete format examples are more reliable than prose descriptions

## When to Add Scripts

Add utility scripts when:

- Operation is deterministic (validation, formatting)
- Same code would be generated repeatedly
- Errors need explicit handling

Use `${CLAUDE_SKILL_DIR}/scripts/` for paths so they resolve from any install location. Scripts save tokens and improve reliability vs generated code.

## When to Split Files

Split into separate files when:

- SKILL.md exceeds 300 lines
- Content has distinct domains (organize by variant in `references/`)
- Advanced features are rarely needed

Tell the agent *when* to load each file: "Read `references/api-errors.md` if the API returns a non-200 status code."

## Skill Content Lifecycle

Once invoked, a skill's content persists for the session. Write standing instructions, not one-time steps. Auto-compaction keeps the first 5,000 tokens per skill within a combined 25,000-token budget across all re-attached skills.

## Review Checklist

After drafting, verify:

- [ ] Description includes triggers ("Use when...")
- [ ] SKILL.md under 300 lines
- [ ] No time-sensitive info (or tucked under "Deprecated" section)
- [ ] Consistent terminology throughout
- [ ] Concrete examples included
- [ ] References one level deep from SKILL.md
- [ ] `allowed-tools` scoped tightly
- [ ] Standing instructions, not one-time steps
