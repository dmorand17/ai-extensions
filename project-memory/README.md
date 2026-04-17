# Claude Skill: Project Memory

A Claude Code skill that sets up and maintains a structured project memory system to track bugs with solutions, architectural decisions, key project facts, and work history.

## Overview

This skill creates a `docs/project_notes/` directory that acts as persistent knowledge for Claude across sessions. It configures `CLAUDE.md` to ensure Claude automatically consults these notes before proposing changes or debugging issues.

**Tracks:**
- **Bugs** — Recurring issues and their solutions
- **Decisions** — Architectural Decision Records (ADRs)
- **Key Facts** — Project configuration, credentials, ports, URLs
- **Issues** — Work log with ticket references

The directory is named `docs/project_notes/` rather than something AI-specific, so it integrates naturally into standard engineering documentation.

## Installation

### Recommended: Symlink Installation

Using a symlink ensures you always have the latest version and can easily pull updates from git:

```bash
# Clone this repository
git clone git@github.com:dmorand17/skill-project-memory.git
cd skill-project-memory

# Claude Code — global installation (recommended)
ln -s $(pwd) ~/.claude/skills/skill-project-memory

# Kiro (IDE and CLI) — global installation
ln -s $(pwd) ~/.kiro/skills/skill-project-memory

# Or for a specific project (Claude Code)
ln -s $(pwd) /path/to/project/.claude/skills/skill-project-memory

# Or for a specific project (Kiro)
ln -s $(pwd) /path/to/project/.kiro/skills/skill-project-memory
```

To update the skill later:
```bash
cd skill-project-memory
git pull
```

In the Kiro IDE, you can also import directly:
1. Open **Agent Steering & Skills** in the Kiro panel
2. Click **+** → **Import a skill**
3. Choose **Local folder** and select the cloned `skill-project-memory` directory

### Alternative: Direct Copy

```bash
git clone git@github.com:dmorand17/skill-project-memory.git
cp -r skill-project-memory ~/.claude/skills/skill-project-memory/
# Or for Kiro
cp -r skill-project-memory ~/.kiro/skills/skill-project-memory/
```

Note: With this method, you'll need to manually copy files again after updates.

## Usage

### Automatic Invocation

The skill activates when Claude detects requests to:
- Set up project memory or a knowledge tracking system
- Log or document a bug fix
- Record an architectural decision
- Update project notes or work history
- Look up whether a problem has been solved before

### Example Prompts

```
"Set up project memory for this repo"
"Log this bug fix so we remember it next time"
"Track the decision we just made about the database schema"
"Update project memory with today's work"
"Initialize a memory system for this project"
```

### Memory Structure Created

```
docs/
└── project_notes/
    ├── bugs.md       # Bug log with solutions
    ├── decisions.md  # Architectural Decision Records
    ├── key_facts.md  # Project configuration and constants
    └── issues.md     # Work log with ticket references
```

## Project Structure

```
skill-project-memory/
└── SKILL.md    # Skill definition with memory setup instructions
```

## Changelog

### Version 1.0.0 (2026-04-03)
- Initial release
- Automated `docs/project_notes/` directory setup
- CLAUDE.md integration for memory-aware protocols
- Bug, decision, key facts, and issues tracking
