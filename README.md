# agent-skills

A collection of skills for Claude Code and Kiro agents.

## Skills

| Skill | Description |
|-------|-------------|
| [bash](./bash/) | Bash script best practices — main function pattern, argument parsing, error handling |
| [skill-creator](./skill-creator/) | Create, improve, and evaluate new skills |
| [git-commit](./git-commit/) | Write git commit messages following Conventional Commits |
| [markdown-convert](./markdown-convert/) | Convert markdown files to other formats using pandoc |
| [project-memory](./project-memory/) | Set up and maintain structured project memory in `docs/project_notes/` |
| [satv2-assessment](./satv2-assessment/) | Deploy and run AWS SATv2 security assessments using Prowler-based scanning via CloudFormation |
| [terraform](./terraform/) | Terraform and OpenTofu best practices |

## Installation

Clone the repo once, then symlink whichever skills you want:

```bash
git clone git@github.com:dmorand17/agent-skills.git
cd agent-skills
```

### Install a single skill

```bash
# Claude Code — global
ln -s $(pwd)/bash ~/.claude/skills/bash
ln -s $(pwd)/terraform ~/.claude/skills/terraform
# ... repeat for other skills

# Kiro — global
ln -s $(pwd)/bash ~/.kiro/skills/bash
ln -s $(pwd)/terraform ~/.kiro/skills/terraform
```

### Install all skills at once

```bash
# Claude Code
for skill in bash skill-creator git-commit markdown-convert project-memory satv2-assessment terraform; do
  ln -sf "$(pwd)/$skill" ~/.claude/skills/$skill
done

# Kiro
for skill in bash skill-creator git-commit markdown-convert project-memory satv2-assessment terraform; do
  ln -sf "$(pwd)/$skill" ~/.kiro/skills/$skill
done
```

### Project-scoped installation

```bash
# Claude Code
ln -s $(pwd)/terraform /path/to/project/.claude/skills/terraform

# Kiro
ln -s $(pwd)/terraform /path/to/project/.kiro/skills/terraform
```

### Updating

```bash
cd agent-skills && git pull
```

Symlinks mean all installed skills update automatically.

## Structure

Each skill directory contains:
- `SKILL.md` — skill definition loaded by the agent
- Additional assets (templates, examples) where applicable

## Credits

- **satv2-assessment** — based on [Running AWS SATv2 Security Assessments with Kiro Skills](https://builder.aws.com/content/3BmTHb9hXqSwqjfG34yEbgURhZY/running-aws-satv2-security-assessments-with-kiro-skills)
