---
name: excalidraw-diagram
description: >
  Create and edit Excalidraw diagrams via MCP live-canvas tools — architecture,
  infrastructure, data flows, service maps, deployment flows, and any technical diagram.
  Use this skill whenever the user wants to draw, sketch, diagram, or visualize a system,
  infrastructure, or flow — including "draw an architecture", "create a diagram", "sketch
  out the system", "make an excalidraw", "diagram this flow", or any request to visualize a
  system or infrastructure topology. Also handles editing existing diagrams, Mermaid
  conversion, iterative refinement, and canvas snapshots. Trigger even if the user doesn't
  say "Excalidraw" — any diagramming request qualifies. Requires the excalidraw MCP server.
---

## Excalidraw Diagram Skill

This skill uses the **excalidraw MCP tools** (`excalidraw/*`) to write to a live canvas with real-time visual verification. If those tools are not in your tool list, prompt the user to set up the server:

> The Excalidraw canvas server is not running. To set up:
> 1. `git clone https://github.com/yctimlin/mcp_excalidraw && cd mcp_excalidraw`
> 2. `npm ci && npm run build`
> 3. `PORT=3000 npm run canvas` then open `http://127.0.0.1:3000` in a browser
> 4. Install the MCP server:
>    `claude mcp add excalidraw -s user -e EXPRESS_SERVER_URL=http://127.0.0.1:3000 -- node /path/to/mcp_excalidraw/dist/index.js`

Full tool list and REST API reference: `references/cheatsheet.md`

---

## Coordinate System

**(0,0) is top-left. x increases rightward, y increases downward.**

| Guideline | Value |
|-----------|-------|
| Vertical tier spacing | 80–120px |
| Horizontal sibling spacing | 40–60px minimum |
| Shape width | `max(160, labelCharCount × 9)` |
| Shape height | 60px (single-line), 80px (two-line) |
| Background zone padding | 50px on all sides |

---

## Layout Anti-Patterns (Critical)

### 1. Never put labels on background zone rectangles

A label bound to a large background zone is centered in the middle — right where your service boxes will be — and cannot be repositioned.

**Wrong:**
```json
{"id": "vpc", "type": "rectangle", "x": 50, "y": 50, "width": 800, "height": 400, "text": "VPC"}
```

**Right — free-standing text element anchored at the top:**
```json
{"id": "vpc",       "type": "rectangle", "x": 50, "y": 50, "width": 800, "height": 400, "backgroundColor": "#e3f2fd"},
{"id": "vpc-label", "type": "text",      "x": 70, "y": 60, "width": 200, "height": 30,  "text": "VPC (10.0.0.0/16)", "fontSize": 18}
```

### 2. Avoid arrows that cross through unrelated zones

Long diagonal arrows through multi-zone diagrams produce unreadable spaghetti. Route arrows along zone perimeters using elbowed or curved paths (see *Arrow Routing*).

### 3. Use arrow labels sparingly

Arrow labels sit at the midpoint and overlap shapes on short arrows. Only label when the relationship is essential (protocol, port number). Keep labels ≤ 12 characters. Omit entirely on dense diagrams.

---

## Default Output

Unless the user says otherwise, every completed diagram produces two files:
1. **`.excalidraw` file** — `export_scene` to `images/<name>.excalidraw`
2. **PNG image** — `export_to_image` with `format: "png"` to `images/<name>.png`

Tell the user the paths when done.

## Workflow: New Diagram

1. Call `read_diagram_guide` for color and sizing best practices.
2. Plan your coordinate grid — map out tiers and x-positions before writing any JSON.
3. Optional: `clear_canvas` to start fresh.
4. `batch_create_elements` — shapes first, then arrows. Use `"text"` for labels; use `startElementId`/`endElementId` for arrow binding (not `x`/`y` coordinates).
5. `set_viewport` with `scrollToContent: true` to fit the view.
6. `get_canvas_screenshot` → run Quality Checklist → fix before continuing.
7. Export: `export_scene` → `export_to_image` (see *Default Output*).

**Example:**
```json
{"elements": [
  {"id": "lb",    "type": "rectangle", "x": 300, "y": 50,  "width": 180, "height": 60, "text": "Load Balancer"},
  {"id": "svc-a", "type": "rectangle", "x": 100, "y": 200, "width": 160, "height": 60, "text": "Web Server 1"},
  {"id": "svc-b", "type": "rectangle", "x": 450, "y": 200, "width": 160, "height": 60, "text": "Web Server 2"},
  {"id": "db",    "type": "rectangle", "x": 275, "y": 350, "width": 210, "height": 60, "text": "PostgreSQL"},
  {"type": "arrow", "x": 0, "y": 0, "startElementId": "lb",    "endElementId": "svc-a"},
  {"type": "arrow", "x": 0, "y": 0, "startElementId": "lb",    "endElementId": "svc-b"},
  {"type": "arrow", "x": 0, "y": 0, "startElementId": "svc-a", "endElementId": "db"},
  {"type": "arrow", "x": 0, "y": 0, "startElementId": "svc-b", "endElementId": "db"}
]}
```

---

## Workflow: Iterative Refinement

`describe_scene` → understand current IDs and positions → make targeted updates → `get_canvas_screenshot` → verify → repeat.

```
batch_create_elements
  → get_canvas_screenshot  ← "text truncated on auth-svc"
  → update_element (increase width)
  → get_canvas_screenshot  ← "overlap between auth-svc and rate-limiter"
  → update_element (reposition)
  → get_canvas_screenshot  ← all checks pass
```

Say "I see [issue], fixing it" — never gloss over visual problems. Only proceed once all checks pass.

## Workflow: Refine an Existing Diagram

1. `describe_scene` — note element IDs and positions.
2. Identify elements by `id` or label text (not by coordinates — they change).
3. `update_element` to resize/recolor/move; `delete_element` to remove.
4. `get_canvas_screenshot` to confirm.
5. If updates fail: check the ID exists with `get_element`; check it's not locked with `unlock_elements`.

## Workflow: Mermaid Conversion

`create_from_mermaid(mermaidDiagram: "graph TD\n  A --> B")` → `set_viewport(scrollToContent: true)` → `get_canvas_screenshot` to verify layout. Reposition with `update_element` if auto-layout is poor.

## Workflow: File I/O & Snapshots

- Export scene: `export_scene` with `filePath` (default: `images/<name>.excalidraw`)
- Export image: `export_to_image` with `format: "png"` and `filePath` (default: `images/<name>.png`) — requires browser
- Import scene: `import_scene` with `mode: "replace"` or `"merge"`
- Shareable link: `export_to_excalidraw_url`
- Snapshot before risky changes: `snapshot_scene` with a name; roll back with `restore_snapshot`

---

## Arrow Routing

Straight arrows can cross through elements. Use curves or elbows when needed:

**Curved** (arc over obstacles):
```json
{"type": "arrow", "points": [[0,0], [50,-40], [200,0]], "roundness": {"type": 2}}
```

**Elbowed** (right-angle / L-shaped):
```json
{"type": "arrow", "points": [[0,0], [0,-50], [200,-50], [200,0]], "elbowed": true}
```

If an arrow would pass through an unrelated shape, add a waypoint to route around it.

---

## Quality Checklist

After each `batch_create_elements`, take a screenshot and check:

- [ ] **Text truncation** — all labels fully visible? Increase `width`/`height` if cut off.
- [ ] **Overlap** — no shapes sharing the same space? Background zones fully contain children with 50px padding.
- [ ] **Arrow crossing** — arrows don't cut through unrelated elements? Route around if needed.
- [ ] **Arrow-label overlap** — arrow labels clear of adjacent shapes?
- [ ] **Spacing** — at least 40px gap between elements.
- [ ] **Readability** — font size ≥ 16 for body, ≥ 20 for titles.
- [ ] **Zone labels** — no labels bound to background rectangles (use free-standing text instead).

---

## Color Palette

| Role | strokeColor | backgroundColor |
|------|-------------|-----------------|
| CI/CD / pipeline | `#1971c2` | `#d0ebff` |
| Build / compute | `#2f9e44` | `#d3f9d8` |
| Storage / data | `#e67700` | `#fff3bf` |
| CDN / edge / network | `#c92a2a` | `#ffe3e3` |
| User / client | `#6741d9` | `#f3f0ff` |
| Generic / neutral | `#495057` | `#f1f3f5` |

---

## Error Recovery

- **Elements off-screen?** `set_viewport` with `scrollToContent: true`.
- **Arrow not connecting?** Verify IDs with `get_element`. Confirm `startElementId`/`endElementId` match real IDs.
- **Canvas bad state?** `snapshot_scene` first, then `clear_canvas` and rebuild. Or `restore_snapshot`.
- **Element won't update?** It may be locked — call `unlock_elements` first.
- **Duplicate text elements?** Find `type: "text"` elements with a `containerId` via `query_elements`, delete the extras. Root cause: labels on background zone rectangles — avoid them.

---

## References

- `references/cheatsheet.md` — Full MCP tool list (26 tools), REST API endpoints, script commands
