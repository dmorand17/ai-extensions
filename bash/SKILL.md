---
name: bash
description: Apply comprehensive bash scripting standards including main function pattern, usage documentation, argument parsing, dependency checking, and error handling. Triggers when creating/editing .sh files, bash scripts, or discussing shell scripting, deployment scripts, automation tasks, or bash conventions.
---

# Bash Best Practices Skill

This skill ensures all bash scripts follow best practices for maintainability, reliability, and user-friendliness.

## When This Skill Applies

This skill should be automatically invoked when:
- Creating new bash scripts or shell scripts
- Editing existing .sh or .bash files
- User requests scripts for automation, deployment, backup, or system tasks
- Reviewing or refactoring bash code
- User mentions: bash, shell script, main function, argument parsing, script structure

## Core Principles

Every script, regardless of size, follows the same structure:

1. **Main function with guard clause** - Always use a `main()` entry point
2. **Usage function** - Document options, dependencies, and examples
3. **Argument parsing** - Structured option handling in main
4. **Dependency checking** - Explicit validation of required tools
5. **Strict error handling** - Use `set -euo pipefail` at the top of every script
6. **Timestamped logging** - `log_*` functions for consistent, auditable output
7. **Function organization** - Single responsibility, correct ordering

## Script Structure

Every script follows this structure:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Script: {{SCRIPT_NAME}}
# Description: {{DESCRIPTION}}

DEPENDENCIES=()  # e.g. (jq curl git)
SCRIPT_NAME=$(basename "$0")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="1.0.0"

log_info()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO  $*"; }
log_debug() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] DEBUG $*"; }
log_warn()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARN  $*"; }
log_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR $*" >&2; }

function usage() {
    cat <<EOF

Brief description of what this script does.

Usage: ${SCRIPT_NAME} [OPTIONS]

Options:
    -i, --input   <file>    Input file to process (required)
    -o, --output  <file>    Output file (optional, defaults to stdout)
    -h, --help              Show this help message
    --version               Show version information

Dependencies: ${DEPENDENCIES[@]}

Examples:
    ${SCRIPT_NAME} -i data.txt -o report.json
    ${SCRIPT_NAME} --input data.txt

EOF
    exit 0
}

function main() {
    local input_file=""
    local output_file=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
        -i | --input)  input_file="$2";  shift 2 ;;
        -o | --output) output_file="$2"; shift 2 ;;
        --version)     echo "${SCRIPT_NAME} version ${VERSION}"; exit 0 ;;
        -h | --help)   usage ;;
        *)
            log_error "Unknown option: $1"
            usage
            ;;
        esac
    done

    [[ -z "$input_file" ]] && log_error "--input is required" && usage

    exit_on_missing_tools "${DEPENDENCIES[@]}"

    log_info "============================================"
    log_info "${SCRIPT_NAME}"
    log_info "  Input:  $input_file"
    log_info "  Output: ${output_file:-stdout}"
    log_info "============================================"

    process_data "$input_file" "$output_file"

    log_info "Done."
}

function process_data() {
    local input_file="$1"
    local output_file="$2"

    log_info "[1/2] Reading input..."
    # implementation

    log_info "[2/2] Writing output..."
    # implementation
}

function exit_on_missing_tools() {
    for cmd in "$@"; do
        if ! command -v "$cmd" &>/dev/null; then
            log_error "Required tool '$cmd' is not installed or not in PATH"
            exit 1
        fi
    done
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
    exit 0
fi
```

## Detailed Best Practices

### 1. Main Function and Guard Clause

Every script has a `main()` function and a guard clause at the end:

```bash
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
    exit 0
fi
```

This enables the script to be safely sourced by other scripts without executing. Always include the explicit `exit 0` after `main`.

### 2. Usage Function

- Defined before `main()`
- Use a heredoc for clean multi-line formatting
- Include: description, options with types, dependencies, examples
- Exit **0** when user explicitly requests help (`-h/--help`)
- Exit **1** (via `usage`) when called due to invalid or missing arguments

### 3. Argument Parsing

Use `while [[ $# -gt 0 ]]` with `shift 2` for options that take a value:

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

Use inline validation for required arguments — concise and easy to scan:

```bash
[[ -z "$COLOR" ]]  && log_error "--color is required"  && usage
[[ -z "$DOMAIN" ]] && log_error "--domain is required" && usage
```

### 4. Dependency Checking

Declare dependencies at the top and check them before use:

```bash
DEPENDENCIES=(jq curl git)

function exit_on_missing_tools() {
    for cmd in "$@"; do
        if ! command -v "$cmd" &>/dev/null; then
            log_error "Required tool '$cmd' is not installed or not in PATH"
            exit 1
        fi
    done
}
```

Show dependencies in `usage()` so users know requirements upfront.

### 5. Error Handling

Use `set -euo pipefail` at the top of every script to catch errors early:

- `set -e` — exit immediately if a command fails
- `set -u` — treat unset variables as errors
- `set -o pipefail` — propagate failures through pipes

```bash
#!/usr/bin/env bash
set -euo pipefail
```

For commands where failure is expected, handle explicitly:

```bash
# Allow a command to fail without triggering set -e
if ! some_command; then
    log_error "some_command failed"
    exit 1
fi

# Or use || to handle inline
cd /some/dir || { log_error "Cannot change to /some/dir"; exit 1; }
```

Rules:
- Always send errors to stderr (the `log_error` function does this)
- Provide context about what failed
- Use meaningful exit codes
- Clean up temporary files on failure via `trap`

### 6. Logging

Use `log_*` functions for all output. Timestamps create an audit trail that's invaluable for automation and CI/CD pipelines:

```bash
log_info()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO  $*"; }
log_debug() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] DEBUG $*"; }
log_warn()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARN  $*"; }
log_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR $*" >&2; }
```

Use `log_info` with step numbering to show progress:

```bash
log_info "[1/3] Tagging SSM parameters..."
log_info "[2/3] Looking up hosted zone..."
log_info "[3/3] Updating alias records..."
log_info "Done."
```

### 7. Function Organization

Order (MANDATORY):
1. `usage()` — first after global declarations
2. `main()` — immediately after usage
3. Business logic functions — core functionality
4. Utility functions — generic helpers

Never add section comment headers like `# UTILITY FUNCTIONS`. The structure speaks for itself.

Function principles:
- Single responsibility per function
- Always use `local` for variables inside functions
- Verb-noun names: `create_backup`, `validate_input`, `get_lb_attr`
- Break down functions longer than ~50 lines

### 8. Code Comments

Comment the *why*, not the *what*. Well-named functions and variables are self-documenting:

```bash
# Bad
# Increment counter
counter=$((counter + 1))

# Good
# Exponential backoff with jitter to prevent thundering herd
delay=$((2 ** attempt * 1000 + RANDOM % 1000))
```

## Script Generation Checklist

- [ ] Shebang: `#!/usr/bin/env bash`
- [ ] `set -euo pipefail` immediately after shebang
- [ ] `DEPENDENCIES` array declared
- [ ] `SCRIPT_DIR` variable defined
- [ ] `log_*` functions defined
- [ ] `usage()` defined before `main()`
- [ ] `main()` handles arg parsing, validation, dependency check, then delegates
- [ ] `exit_on_missing_tools` called in `main()`
- [ ] Guard clause at end of file
- [ ] `set -euo pipefail` present at top of script
- [ ] `local` used for all function variables
- [ ] Errors go to stderr via `log_error`
- [ ] Meaningful exit codes

## Common Patterns

### Temporary Files

```bash
temp_file=$(mktemp)
trap "rm -f '$temp_file'" EXIT

temp_dir=$(mktemp -d)
trap "rm -rf '$temp_dir'" EXIT
```

### Interactive Confirmation

```bash
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Cancelled."
    exit 0
fi
```

### Pipeline Error Handling

With `set -o pipefail` enabled, pipeline failures are caught automatically. For cases where you need to inspect individual stages:

```bash
command1 | command2
if [[ "${PIPESTATUS[0]}" -ne 0 ]]; then
    log_error "command1 failed"
    exit 1
fi
```

## Testing

Always verify generated scripts:
1. **Syntax**: `bash -n script.sh`
2. **Lint**: `shellcheck script.sh` (if installed)
3. **Help**: `./script.sh --help`
4. **Missing args**: `./script.sh` (should show usage)
5. **Missing tools**: remove a dependency and verify the error message
6. **Sourcing**: `source script.sh` (should not execute)
