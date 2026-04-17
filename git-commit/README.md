# Claude Skill: Git Commit

A Claude Code skill that helps write, format, and review git commit messages following the Conventional Commits specification.

## Overview

This skill activates when you need help crafting a well-structured commit message. It enforces consistent formatting across all commit types and provides guidance on scope, subject, body, and footer conventions.

**Covers:**
- Conventional Commits format (type, scope, subject)
- Full type reference (feat, fix, docs, style, refactor, and more)
- Body and footer conventions
- Breaking change notation

## Installation

### Recommended: Symlink Installation

Using a symlink ensures you always have the latest version and can easily pull updates from git:

```bash
# Clone this repository
git clone git@github.com:dmorand17/skill-git-commit.git
cd skill-git-commit

# Claude Code — global installation (recommended)
ln -s $(pwd) ~/.claude/skills/skill-git-commit

# Kiro (IDE and CLI) — global installation
ln -s $(pwd) ~/.kiro/skills/skill-git-commit

# Or for a specific project (Claude Code)
ln -s $(pwd) /path/to/project/.claude/skills/skill-git-commit

# Or for a specific project (Kiro)
ln -s $(pwd) /path/to/project/.kiro/skills/skill-git-commit
```

To update the skill later:
```bash
cd skill-git-commit
git pull
```

In the Kiro IDE, you can also import directly:
1. Open **Agent Steering & Skills** in the Kiro panel
2. Click **+** → **Import a skill**
3. Choose **Local folder** and select the cloned `skill-git-commit` directory

### Alternative: Direct Copy

```bash
git clone git@github.com:dmorand17/skill-git-commit.git
cp -r skill-git-commit ~/.claude/skills/skill-git-commit/
# Or for Kiro
cp -r skill-git-commit ~/.kiro/skills/skill-git-commit/
```

Note: With this method, you'll need to manually copy files again after updates.

## Usage

### Automatic Invocation

The skill activates when Claude detects requests to:
- Write or generate a commit message
- Format or clean up an existing commit message
- Review a commit message for correctness
- Help phrase a commit

### Example Prompts

```
"Write a commit message for these changes"
"I added user authentication with JWT — what's the commit message?"
"Format this as a conventional commit: updated login page styles"
"Review my commit message and suggest improvements"
```

### Example Output

Input: `"added user auth with JWT tokens"`
Output: `feat(auth): implement JWT-based authentication`

## Project Structure

```
skill-git-commit/
└── SKILL.md    # Skill definition with Conventional Commits conventions
```

## Changelog

### Version 1.0.0 (2026-04-03)
- Initial release
- Conventional Commits format (header, body, footer)
- Full type reference table
- Breaking change and footer conventions
- Merged from commit-message-formatter and git-commit-helper skills
