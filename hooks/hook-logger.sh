#!/usr/bin/env bash
set -euo pipefail

# Script: hook-logger.sh
# Description: Transparent Claude Code hook payload logger. Reads the JSON
#              payload Claude Code passes on stdin, appends a timestamped
#              entry to a log file, and exits 0 so it never blocks the hook
#              chain. Intended as a debugging sidecar while building hooks.
# Author: Doug Morand
# Date: 2026-05-15

DEPENDENCIES=()  # jq is optional and handled gracefully if missing
SCRIPT_NAME=$(basename "$0")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_LOG_FILE="${HOME}/.claude/logs/hook-debug.log"

log_info()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO  $*"; }
log_debug() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] DEBUG $*"; }
log_warn()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARN  $*" >&2; }
log_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR $*" >&2; }

function usage() {
    cat <<EOF

Claude Code hook payload logger.

Reads the JSON payload Claude Code passes to a hook on stdin and appends a
timestamped entry (header + pretty-printed JSON) to a log file. Always exits
0 so it can be safely chained with other hooks without blocking.

Usage: ${SCRIPT_NAME} [OPTIONS]

Options:
    -f, --log-file <path>   Log file path (default: ${DEFAULT_LOG_FILE})
    -h, --help              Show this help message and exit

Environment:
    HOOK_LOGGER_FILE        Override default log path (lower precedence than --log-file)

Dependencies: jq (optional — falls back to raw JSON if not installed)

Example settings.json snippet (logs every PreToolUse event):

    {
      "hooks": {
        "PreToolUse": [
          {
            "matcher": "",
            "hooks": [
              { "type": "command", "command": "\$HOME/.claude/hooks/hook-logger.sh" }
            ]
          }
        ]
      }
    }

To target a specific event, replace "PreToolUse" with any hook event name
(SessionStart, PostToolUse, Stop, UserPromptSubmit, etc.). To narrow by tool,
set "matcher" (e.g. "Bash" or "Edit|Write").

Smoke test:
    echo '{"hook_event_name":"PreToolUse","tool_name":"Bash"}' | ${SCRIPT_NAME}
    tail -n 20 ${DEFAULT_LOG_FILE}

EOF
    exit 0
}

function main() {
    local log_file="${HOOK_LOGGER_FILE:-$DEFAULT_LOG_FILE}"

    while [[ $# -gt 0 ]]; do
        case "$1" in
        -f | --log-file) log_file="$2"; shift 2 ;;
        -h | --help) usage ;;
        *)
            log_error "Unknown option: $1"
            usage
            ;;
        esac
    done

    exit_on_missing_tools "${DEPENDENCIES[@]+"${DEPENDENCIES[@]}"}"

    mkdir -p "$(dirname "$log_file")"

    local payload
    payload=$(cat)

    write_log_entry "$log_file" "$payload"

    exit 0
}

function write_log_entry() {
    local log_file="$1"
    local payload="$2"
    local event_name="UNKNOWN"
    local timestamp
    timestamp=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

    if command -v jq &>/dev/null && [ -n "$payload" ]; then
        event_name=$(printf '%s' "$payload" | jq -r '.hook_event_name // "UNKNOWN"' 2>/dev/null || echo "UNKNOWN")
    fi

    {
        echo "===== ${timestamp} [${event_name}] ====="
        if command -v jq &>/dev/null && [ -n "$payload" ]; then
            printf '%s' "$payload" | jq . 2>/dev/null || printf '%s\n' "$payload"
        else
            printf '%s\n' "$payload"
        fi
        echo ""
    } >> "$log_file"
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
