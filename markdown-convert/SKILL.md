---
name: markdown-convert
description: Convert markdown files to other formats using pandoc. Use this skill whenever the user wants to export, convert, or transform a markdown file — even if they say things like "make a Word doc from this", "export to PDF", "save as HTML", "convert to docx", "I need to share this as a PDF", or similar. Supports docx, pdf, and html output.
---

# Markdown Converter

Convert a markdown file to docx, pdf, or html using pandoc.

## Workflow

1. **Identify the input file** — the user will provide a path. If it's relative, resolve it from their working directory. If the path is ambiguous, ask.

2. **Determine the output format** — infer from the user's request:
   - "Word" / "docx" / "document" → `docx`
   - "PDF" / "pdf" → `pdf`
   - "HTML" / "web" / "webpage" → `html`
   - If unclear, ask: "Which format — docx, pdf, or html?"

3. **Determine the output path** — default to the same directory as the input file, with the appropriate extension. If the user specifies a different output path or name, use that.

4. **Run pandoc** — use the Bash tool to execute the conversion command.

5. **Confirm success** — tell the user the output file path.

---

## Pandoc Commands

### docx
```bash
pandoc "<input.md>" -o "<output.docx>"
```

### html
```bash
pandoc "<input.md>" -o "<output.html>" --standalone
```

### pdf
PDF requires a PDF engine. Try engines in this order until one succeeds:

```bash
# Try 1: xelatex (most common with TeX distributions)
pandoc "<input.md>" -o "<output.pdf>" --pdf-engine=xelatex

# Try 2: pdflatex
pandoc "<input.md>" -o "<output.pdf>" --pdf-engine=pdflatex

# Try 3: weasyprint
pandoc "<input.md>" -o "<output.pdf>" --pdf-engine=weasyprint
```

Check which engines are available first:
```bash
which xelatex pdflatex weasyprint 2>/dev/null
```

If no PDF engine is found, tell the user: "PDF conversion requires a LaTeX distribution (e.g. MacTeX, TinyTeX) or weasyprint. For the quickest install: `brew install --cask mactex-no-gui` or `pip install weasyprint`."

---

## YAML Frontmatter

Pandoc reads YAML frontmatter automatically. The `title`, `author`, and `date` fields become document metadata (title page in docx/pdf, `<title>` tag in html). No special handling needed — pandoc handles this natively.

---

## Notes

- Always quote file paths in the bash command to handle spaces.
- If pandoc returns an error, show the error message to the user and suggest a fix (missing engine, unsupported syntax, etc.).
- If the user asks to convert multiple files, handle them sequentially and confirm each one.
