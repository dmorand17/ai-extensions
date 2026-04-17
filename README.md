# agent-skills

A collection of skills for Claude Code and Kiro agents.

## Skills

| Skill | Description |
|-------|-------------|
| [bash](./bash/) | Bash script best practices — main function pattern, argument parsing, error handling |
| [creator](./creator/) | Create, improve, and evaluate new skills |
| [git-commit](./git-commit/) | Write git commit messages following Conventional Commits |
| [markdown-convert](./markdown-convert/) | Convert markdown files to other formats using pandoc |
| [project-memory](./project-memory/) | Set up and maintain structured project memory in `docs/project_notes/` |
| [terraform](./terraform/) | Terraform and OpenTofu best practices |

## Structure

Each skill directory contains:
- `SKILL.md` — skill definition loaded by the agent
- `README.md` — usage documentation
- Additional assets (templates, examples) where applicable
