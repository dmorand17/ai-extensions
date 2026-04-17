# Claude Skill: Skill Creator

A Claude Code skill for creating new skills, iteratively improving existing ones, running evaluations, and optimizing skill descriptions for better triggering accuracy.

## Overview

This skill guides you through the full skill development lifecycle:

1. **Capture Intent** — Define what the skill should do and when it should trigger
2. **Draft the Skill** — Write `SKILL.md` with frontmatter, instructions, and bundled resources
3. **Run Evaluations** — Test the skill against real prompts, with and without the skill active
4. **Review Results** — Qualitative output review via a browser-based viewer + quantitative benchmarks
5. **Iterate** — Improve based on feedback, rerun, repeat until satisfied
6. **Optimize Description** — Run the description optimizer to improve triggering accuracy
7. **Package** — Bundle the skill for distribution as a `.skill` file

## Installation

### Recommended: Symlink Installation

Using a symlink ensures you always have the latest version and can easily pull updates from git:

```bash
# Clone this repository
git clone git@github.com:dmorand17/skill-creator.git
cd skill-creator

# Claude Code — global installation (recommended)
ln -s $(pwd) ~/.claude/skills/skill-creator

# Kiro (IDE and CLI) — global installation
ln -s $(pwd) ~/.kiro/skills/skill-creator

# Or for a specific project (Claude Code)
ln -s $(pwd) /path/to/project/.claude/skills/skill-creator

# Or for a specific project (Kiro)
ln -s $(pwd) /path/to/project/.kiro/skills/skill-creator
```

To update the skill later:
```bash
cd skill-creator
git pull
```

In the Kiro IDE, you can also import directly:
1. Open **Agent Steering & Skills** in the Kiro panel
2. Click **+** → **Import a skill**
3. Choose **Local folder** and select the cloned `skill-creator` directory

### Alternative: Direct Copy

```bash
git clone git@github.com:dmorand17/skill-creator.git
cp -r skill-creator ~/.claude/skills/skill-creator/
# Or for Kiro
cp -r skill-creator ~/.kiro/skills/skill-creator/
```

Note: With this method, you'll need to manually copy files again after updates.

## Usage

### Automatic Invocation

The skill activates when Claude detects requests to:
- Create a new skill from scratch
- Edit or improve an existing skill
- Run evaluations or benchmarks on a skill
- Optimize a skill's description for triggering accuracy
- Package a skill for distribution

### Example Prompts

```
"Create a new skill for formatting SQL queries"
"I want to turn this workflow into a skill"
"Improve my existing terraform skill"
"Run evals on this skill and show me the results"
"Optimize the description of my skill so it triggers more reliably"
```

## Project Structure

```
skill-creator/
├── SKILL.md           # Skill definition — full development lifecycle instructions
└── skill-creator.md   # Extended reference guide for skill creation
```

## Changelog

### Version 1.0.0 (2026-04-03)
- Initial release
- Full skill creation lifecycle (draft → eval → iterate → optimize → package)
- Eval viewer for qualitative and quantitative review
- Description optimization via automated triggering loop
- Support for Claude Code, Claude.ai, and Cowork environments
