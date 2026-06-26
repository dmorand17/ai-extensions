<p align="center">
  <img src="docs/img/ai-extensions.png" alt="ai-extensions logo">
</p>

<h1 align="center">ai-extensions</h1>

<p align="center">
  <em>Personal collection of Claude Code skills, agents, and hooks</em>
</p>

<hr/>

A curated set of [Claude Code](https://docs.claude.com/en/docs/claude-code) extensions — self-contained skills, subagent definitions, and hook scripts — that you can symlink into your global or project-scoped Claude config.

## 🚀 Quick start

```bash
git clone git@github.com:dmorand17/ai-extensions.git
cd ai-extensions
ln -s $(pwd)/skills/git-flow ~/.claude/skills/git-flow   # symlink one skill
```

## 🧩 Skills

| Skill | Description |
|-------|-------------|
| [git-flow](./skills/git-flow/) | Conventional Commits + full ship flow on request (branch, commit, push, open PR) |
| [release-generator](./skills/release-generator/) | Cut a GitHub release — suggest the next semver tag, generate categorized release notes, and publish via `gh release create` (or just generate changelogs/notes) |
| [excalidraw-diagram](./skills/excalidraw-diagram/) | Create and edit Excalidraw diagrams via MCP |
| [markdown-convert](./skills/markdown-convert/) | Convert markdown files to other formats using pandoc |
| [skill-creator](./skills/skill-creator/) | Create, improve, and evaluate new skills |
| [handoff](./skills/handoff/) | Compact the current conversation into a handoff document for another agent to pick up |
| [caveman](./skills/caveman/) | Ultra-compressed communication mode — cuts token usage ~75% by dropping filler while keeping full technical accuracy |
| [grill-me](./skills/grill-me/) | Interview the user relentlessly about a plan or design until reaching shared understanding |
| [grill-me-with-docs](./skills/grill-me-with-docs/) | Grilling session that challenges plans against the domain model, sharpens terminology, and updates CONTEXT.md/ADRs inline |
| [project-memory](./skills/project-memory/) | Set up and maintain structured project memory in `docs/project_notes/` |
| [satv2-assessment](./skills/satv2-assessment/) | Deploy and run AWS SATv2 security assessments using Prowler-based scanning |
| [image-enhancer](./skills/image-enhancer/) | Enhance image quality — sharpen, upscale, denoise, and clean up compression artifacts |

## 🤖 Agents

| Agent | Description |
|-------|-------------|
| [architecture-reviewer](./agents/architecture-reviewer.md) | Reviews system architecture and design decisions |
| [code-reviewer](./agents/code-reviewer.md) | Reviews code for quality, correctness, and style |
| [docs-explorer](./agents/docs-explorer.md) | Explores and explains documentation |
| [security-auditor](./agents/security-auditor.md) | Audits code and infrastructure for security issues |

## 🪝 Hooks

| Hook | Description |
|------|-------------|
| [hook-logger.sh](./hooks/hook-logger.sh) | Logs hook events for debugging extension authoring |

<details>
<summary><strong>hook-logger.sh</strong> — usage</summary>

Transparent payload logger for Claude Code hooks. Reads the JSON payload from stdin, appends a timestamped entry to a log file, and always exits 0 so it never blocks the hook chain. Useful as a debugging sidecar while building or troubleshooting hooks.

#### Setup

Add to your `settings.json` (or `.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "$HOME/.claude/hooks/hook-logger.sh" }
        ]
      }
    ]
  }
}
```

Replace `PreToolUse` with any hook event (`SessionStart`, `PostToolUse`, `Stop`, `UserPromptSubmit`, etc.). Narrow by tool with `"matcher": "Bash"` or `"matcher": "Edit|Write"`.

#### Options

| Flag | Default | Description |
|------|---------|-------------|
| `-f, --log-file <path>` | `~/.claude/logs/hook-debug.log` | Log file path |
| `HOOK_LOGGER_FILE` env var | (same) | Override default path (lower precedence than `-f`) |

#### Smoke test

```bash
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash"}' | ./hooks/hook-logger.sh
tail -n 20 ~/.claude/logs/hook-debug.log
```

Requires `jq` for pretty-printed output (falls back to raw JSON if missing).

</details>

## 📦 Installation

Clone the repo (if you haven't already):

```bash
git clone git@github.com:dmorand17/ai-extensions.git
cd ai-extensions
```

Symlink an individual skill into your global skills dir:

```bash
ln -s $(pwd)/skills/git-flow ~/.claude/skills/git-flow   # or ~/.kiro/skills/...
```

Symlink everything:

```bash
for skill in skills/*/; do
  ln -sf "$(pwd)/$skill" ~/.claude/skills/$(basename "$skill")
done
for agent in agents/*.md; do
  ln -sf "$(pwd)/$agent" ~/.claude/agents/$(basename "$agent")
done
for hook in hooks/*/; do
  ln -sf "$(pwd)/$hook" ~/.claude/hooks/$(basename "$hook")
done
```

Project-scoped install:

```bash
ln -s $(pwd)/skills/skill-creator /path/to/project/.claude/skills/skill-creator
```

### Updating

```bash
cd ai-extensions && git pull
```

Symlinks pick up updates automatically.

## 🗂️ Structure

```
skills/        # Self-contained skill packages, each with a SKILL.md
agents/        # Subagent definitions (one .md file each)
hooks/         # Hook scripts
```

Each skill directory contains `SKILL.md` plus any templates, examples, or references it needs.

## 🔗 Useful external skills

Skills from other authors that pair well with this repo:

| Name | Author | Description |
|------|--------|-------------|
| [caveman](https://github.com/JuliusBrussee/caveman) | JuliusBrussee | Ultra-compressed communication mode plus a `caveman-compress` skill that compresses memory files (CLAUDE.md, todos) to save input tokens |

## 💡 Inspiration

Projects and writing that shaped how skills here are designed:

| Source | Why |
|--------|-----|
| [mattpocock/skills](https://github.com/mattpocock/skills) | Productivity and engineering skills — caveman, grill-me, handoff, grill-with-docs |

## 🙏 Credits

- **satv2-assessment** — based on [Running AWS SATv2 Security Assessments with Kiro Skills](https://builder.aws.com/content/3BmTHb9hXqSwqjfG34yEbgURhZY/running-aws-satv2-security-assessments-with-kiro-skills)
