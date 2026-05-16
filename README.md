# ai-extensions

Skills (and eventually subagents, hooks, and commands) for Claude Code and Kiro.

The repo follows the [Claude Code plugin layout](https://docs.claude.com/en/docs/claude-code/plugins) — typed top-level directories (`skills/`, later `agents/`, `hooks/`, `commands/`) — so it can become a plugin in place when ready.

## Skills

| Skill | Description |
|-------|-------------|
| [changelog-generator](./skills/changelog-generator/) | Generate user-facing changelogs and release notes from git commit history |
| [excalidraw-diagram](./skills/excalidraw-diagram/) | Create and edit Excalidraw diagrams via MCP |
| [git-commit](./skills/git-commit/) | Stage and commit using Conventional Commits (or just draft/review a message) |
| [image-enhancer](./skills/image-enhancer/) | Enhance image quality — sharpen, upscale, denoise, and clean up compression artifacts |
| [markdown-convert](./skills/markdown-convert/) | Convert markdown files to other formats using pandoc |
| [project-memory](./skills/project-memory/) | Set up and maintain structured project memory in `docs/project_notes/` |
| [satv2-assessment](./skills/satv2-assessment/) | Deploy and run AWS SATv2 security assessments using Prowler-based scanning via CloudFormation |
| [skill-creator](./skills/skill-creator/) | Create, improve, and evaluate new skills |

> Reference docs (Terraform conventions, bash standards, etc.) live in the companion repo: [dmorand17/ai-config](https://github.com/dmorand17/ai-config).

## Installation

```bash
git clone git@github.com:dmorand17/ai-extensions.git
cd ai-extensions
```

### Install a single skill

```bash
# Claude Code — global
ln -s $(pwd)/skills/git-commit ~/.claude/skills/git-commit

# Kiro — global
ln -s $(pwd)/skills/git-commit ~/.kiro/skills/git-commit
```

### Install all skills at once

```bash
# Claude Code
for skill in skills/*/; do
  name=$(basename "$skill")
  ln -sf "$(pwd)/$skill" ~/.claude/skills/$name
done

# Kiro
for skill in skills/*/; do
  name=$(basename "$skill")
  ln -sf "$(pwd)/$skill" ~/.kiro/skills/$name
done
```

### Project-scoped installation

```bash
# Claude Code
ln -s $(pwd)/skills/skill-creator /path/to/project/.claude/skills/skill-creator

# Kiro
ln -s $(pwd)/skills/skill-creator /path/to/project/.kiro/skills/skill-creator
```

### Updating

```bash
cd ai-extensions && git pull
```

Symlinks mean all installed skills update automatically.

## Structure

```
skills/                # Self-contained skill packages, each with a SKILL.md
agents/   (planned)    # Subagent definitions
hooks/    (planned)    # Hook scripts
commands/ (planned)    # Slash commands
```

Each skill directory contains:
- `SKILL.md` — skill definition loaded by the agent
- Additional assets (templates, examples, references) where applicable

## Credits

- **satv2-assessment** — based on [Running AWS SATv2 Security Assessments with Kiro Skills](https://builder.aws.com/content/3BmTHb9hXqSwqjfG34yEbgURhZY/running-aws-satv2-security-assessments-with-kiro-skills)
