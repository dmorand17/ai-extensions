#!/usr/bin/env bash
set -euo pipefail

# Script: {{SCRIPT_NAME}}
# Description: {{DESCRIPTION}}
# Author: {{AUTHOR}}
# Date: {{DATE}}

DEPENDENCIES=()  # Add required external tools: (jq curl git)
SCRIPT_NAME=$(basename "$0")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="1.0.0"

log_info()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO  $*"; }
log_debug() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] DEBUG $*"; }
log_warn()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARN  $*"; }
log_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR $*" >&2; }

function usage() {
    cat <<EOF

{{DESCRIPTION}}

Usage: ${SCRIPT_NAME} [OPTIONS]

Options:
    -i, --input   <file>    Input file to process (required)
    -o, --output  <file>    Output file (optional, defaults to stdout)
    -h, --help              Show this help message
    --version               Show version information

Dependencies: ${DEPENDENCIES[@]}

Examples:
    ${SCRIPT_NAME} -i data.txt -o result.txt
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
        --version)
            echo "${SCRIPT_NAME} version ${VERSION}"
            exit 0
            ;;
        -h | --help) usage ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            ;;
        esac
    done

    [[ -z "$input_file" ]] && echo "Error: --input is required" >&2 && usage

    exit_on_missing_tools "${DEPENDENCIES[@]}"

    log_info "============================================"
    log_info "{{SCRIPT_NAME}}"
    log_info "============================================"
    log_info "  Input:  $input_file"
    log_info "  Output: ${output_file:-stdout}"
    log_info "============================================"

    process_data "$input_file" "$output_file"

    log_info "Done."
}

function process_data() {
    local input_file="$1"
    local output_file="$2"

    log_info "[1/2] Reading input data..."
    if [ ! -f "$input_file" ]; then
        log_error "Input file not found: $input_file"
        exit 1
    fi
    local data
    data=$(cat "$input_file")

    log_info "[2/2] Writing output..."
    # TODO: Add actual processing logic
    local result="$data"

    if [ -n "$output_file" ]; then
        echo "$result" > "$output_file"
    else
        echo "$result"
    fi
}

function exit_on_missing_tools() {
    for cmd in "$@"; do
        if ! command -v "$cmd" &>/dev/null; then
            printf "Error: Required tool '%s' is not installed or not in PATH\n" "$cmd" >&2
            exit 1
        fi
    done
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
    exit 0
fi
