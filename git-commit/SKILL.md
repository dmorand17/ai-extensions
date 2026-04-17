---
name: git-commit
description: >
  Help write git commit messages using standard git conventions. Use this skill
  when the user asks to write, generate, format, or review a git commit message,
  or when they need help phrasing a commit. Do NOT use for branches, PRs,
  merges, or other git operations — only for commit message writing.
---

## Git Commit Conventions

Follow the Conventional Commits specification.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

- Header (type, scope, subject) is mandatory; body and footer are optional
- No line should exceed 72 characters (100 max)
- Blank line between header, body, and footer

### Types

| Type       | Purpose                                          |
|------------|--------------------------------------------------|
| `feat`     | New feature or note                              |
| `fix`      | Bug fix or correction                            |
| `docs`     | Documentation-only changes                       |
| `style`    | Formatting (no content changes)                  |
| `refactor` | Restructuring without adding/removing content    |
| `test`     | Adding tests                                     |
| `chore`    | Build process or auxiliary tool changes          |
| `build`    | Build-related changes                            |
| `ci`       | CI-related changes                               |
| `perf`     | Performance improvements                         |
| `revert`   | Reverting changes                                |

### Guidelines

- Use imperative mood: "add" not "added" or "adds"
- Don't capitalize the first letter of the subject
- No period at the end of the subject
- Scope is optional but recommended (e.g., folder name or topic area)
- Body explains what and why, not how
- Breaking changes: add `!` after type/scope
- Reference issues in footer: `Closes #123`

### Example

Input: "added user auth with JWT tokens"
Output: `feat(auth): implement JWT-based authentication`
