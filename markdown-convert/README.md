# skill-markdown-convert

A Claude Code skill that converts markdown files to other formats using pandoc.

## Supported Output Formats

- **docx** — Microsoft Word document
- **pdf** — PDF (requires a LaTeX distribution or weasyprint)
- **html** — Standalone HTML file

## Usage

Trigger this skill by asking Claude to convert or export a markdown file:

- "Convert this markdown to a Word doc"
- "Export README.md to PDF"
- "Save this as HTML"
- "Make a docx from this file"

## Requirements

- [pandoc](https://pandoc.org/installing.html)
- For PDF output: [MacTeX](https://www.tug.org/mactex/) / [TinyTeX](https://yihui.org/tinytex/) or [weasyprint](https://weasyprint.org/)

```bash
brew install pandoc
brew install --cask mactex-no-gui  # for PDF support
```

## Installation

Copy `SKILL.md` into your Claude Code skills directory:

```bash
cp SKILL.md ~/.claude/skills/markdown-convert/SKILL.md
```
