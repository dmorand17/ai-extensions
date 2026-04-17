# Claude Skill: Bash Best Practices

A Claude Code skill that ensures bash scripts follow best practices for
maintainability, reliability, and user-friendliness.

## Overview

This skill automatically activates when working with bash scripts to enforce a
single consistent structure — regardless of script size or complexity.

Every script uses:
- `main()` function with guard clause
- `usage()` for help and argument documentation
- Compact `shift 2` argument parsing
- Timestamped `log_*` functions for auditable output
- Explicit error handling (no `set -e`)

## Features

- **Automatic Activation**: Triggers when creating or editing bash scripts
- **Consistent Structure**: One pattern for all scripts — no decision trees
- **Timestamped Logging**: `log_info/log_debug/log_warn/log_error` with ISO timestamps

## Installation

### Recommended: Symlink Installation

Using a symlink ensures you always have the latest version and can easily pull updates from git:

```bash
# Clone this repository
git clone git@github.com:dmorand17/skill-bash.git
cd skill-bash

# Claude Code — global installation (recommended)
ln -s $(pwd) ~/.claude/skills/skill-bash

# Kiro (IDE and CLI) — global installation
ln -s $(pwd) ~/.kiro/skills/skill-bash

# Or for a specific project (Claude Code)
ln -s $(pwd) /path/to/project/.claude/skills/skill-bash

# Or for a specific project (Kiro)
ln -s $(pwd) /path/to/project/.kiro/skills/skill-bash
```

To update the skill later:
```bash
cd skill-bash
git pull
```

In the Kiro IDE, you can also import directly:
1. Open **Agent Steering & Skills** in the Kiro panel
2. Click **+** → **Import a skill**
3. Choose **Local folder** and select the cloned `skill-bash` directory

### Alternative: Direct Copy

```bash
git clone git@github.com:dmorand17/skill-bash.git
cp -r skill-bash ~/.claude/skills/skill-bash/
# Or for Kiro
cp -r skill-bash ~/.kiro/skills/skill-bash/
```

Note: With this method, you'll need to manually copy files again after updates.

## Usage

### Automatic Invocation

The skill activates when Claude detects:
- Creating or editing `.sh` / `.bash` files
- Requests for automation, deployment, or backup scripts
- Mentions of bash, shell scripting, or script structure

### Example Prompts

```
"Create a deployment script for my ECS service"
"Review scripts/post-install.sh for best practices"
"Write a script to rotate AWS credentials"
"Make this bash script more maintainable"
```

## Project Structure

```
skill-bash/
├── SKILL.md                  # Skill definition and all best practices
├── templates/
│   └── script-template.sh   # Unified script template
└── README.md
```

## Key Patterns

### Timestamped Logging

All output goes through `log_*` functions, providing an audit trail for CI/CD
and automation pipelines:

```bash
log_info()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO  $*"; }
log_debug() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] DEBUG $*"; }
log_warn()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARN  $*"; }
log_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR $*" >&2; }
```

Use `log_info` with step numbering for progress:
```bash
log_info "[1/3] Tagging SSM parameters..."
log_info "[2/3] Looking up hosted zone..."
log_info "[3/3] Updating alias records..."
```

### Argument Parsing

```bash
while [[ $# -gt 0 ]]; do
    case "$1" in
    -c | --color)   COLOR="$2";  shift 2 ;;
    -d | --domain)  DOMAIN="$2"; shift 2 ;;
    -v | --verbose) verbose=true; shift  ;;
    -h | --help)    usage                ;;
    *)
        log_error "Unknown option: $1"
        usage
        ;;
    esac
done
```

### Inline Validation

```bash
[[ -z "$COLOR" ]]  && log_error "--color is required"  && usage
[[ -z "$DOMAIN" ]] && log_error "--domain is required" && usage
```

### Guard Clause

```bash
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
    exit 0
fi
```

## Testing Generated Scripts

```bash
# Syntax check
bash -n script.sh

# Lint
shellcheck script.sh

# Help output
./script.sh --help

# Missing required arg
./script.sh
```

## Troubleshooting

**Skill not activating?**
1. Verify the symlink: `ls ~/.claude/skills/bash/`
2. Check `SKILL.md` frontmatter is valid YAML
3. Try explicit mention: "Apply bash best practices to this script"

