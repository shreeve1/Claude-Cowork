---
name: excalidraw-diagram
description: Create Excalidraw diagrams as `.excalidraw` JSON scenes with a local editor URL, standalone HTML fallback and optional PNG previews. Use when user asks for Excalidraw, diagram, flowchart, architecture diagram, workflow visualization, or visual explanation.
---


# Excalidraw Diagram Creator

Create diagrams as `.excalidraw` JSON scenes, preview them in a local editor, and deliver the standalone HTML (plus optional PNG) previews.


- Source scene: `artifacts/diagrams/<name>.excalidraw`
- Deliverables: local editor URL, `artifacts/diagrams/<name>.html`, optional `.png`

If the user names a folder (e.g. `clients/<client>/`), use it instead of `artifacts/diagrams/`.

Keep chat responses concise. Lead with artifact paths.


## Fallback preview: local Excalidraw editor URL

Use when an agent-viewable preview is needed. Requires Python.

Start the local editor server and open the printed URL in a browser. It loads the real Excalidraw editor and avoids `file://` sibling-fetch failures.

From workspace root, start server in background and write the URL to a workspace artifact:

macOS/Linux shell:

```bash
python3 .claude/skills/excalidraw-diagram/scripts/export_to_excalidraw_url.py artifacts/diagrams/my-diagram.excalidraw --port 0 --url-file artifacts/diagrams/my-diagram.url > artifacts/diagrams/my-diagram.server.log 2>&1 &
```

Windows PowerShell:

```powershell
Start-Process py -ArgumentList '.claude\skills\excalidraw-diagram\scripts\export_to_excalidraw_url.py','artifacts\diagrams\my-diagram.excalidraw','--port','0','--url-file','artifacts\diagrams\my-diagram.url' -RedirectStandardOutput 'artifacts\diagrams\my-diagram.server.log' -RedirectStandardError 'artifacts\diagrams\my-diagram.server.err.log'
```

Read `artifacts/diagrams/<name>.url`, then open that exact `http://127.0.0.1:<port>` URL in a browser.

If Python is unavailable, create standalone HTML fallback instead.

## Standalone HTML fallback

Create this when Python is unavailable, when a persistent local server is not desired, or when user wants a downloadable preview that works from `file://`:

- `artifacts/diagrams/<name>.html`

The `.html` preview must use browser-native SVG/JS only and embed scene JSON directly in the file. Do not use `fetch()` to load a sibling `.excalidraw`; browsers block that under `file://`. Use `references/html-preview-template.html` as the starting point and replace the `SCENE_DATA_PLACEHOLDER` token with the full scene JSON.

The `.excalidraw` file can always be opened manually in <https://excalidraw.com>.

## Optional PNG setup

PNG export is optional. Use only when local tools exist.

### Preferred: uv available

From workspace root:

macOS/Linux shell:

```bash
cd .claude/skills/excalidraw-diagram/scripts && uv sync && uv run playwright install chromium
```

Windows PowerShell:

```powershell
cd .claude\skills\excalidraw-diagram\scripts; uv sync; uv run playwright install chromium
```

Render:

macOS/Linux shell:

```bash
cd .claude/skills/excalidraw-diagram/scripts && uv run python render_excalidraw.py ../../../../artifacts/diagrams/my-diagram.excalidraw
```

Windows PowerShell:

```powershell
cd .claude\skills\excalidraw-diagram\scripts; uv run python render_excalidraw.py ..\..\..\..\artifacts\diagrams\my-diagram.excalidraw
```

### Fallback: Python available, uv missing

macOS/Linux shell:

```bash
cd .claude/skills/excalidraw-diagram/scripts
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install playwright
python -m playwright install chromium
```

Windows PowerShell:

```powershell
cd .claude\skills\excalidraw-diagram\scripts
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install playwright
python -m playwright install chromium
```

Render:

macOS/Linux shell:

```bash
cd .claude/skills/excalidraw-diagram/scripts
. .venv/bin/activate
python render_excalidraw.py ../../../../artifacts/diagrams/my-diagram.excalidraw
```

Windows PowerShell:

```powershell
cd .claude\skills\excalidraw-diagram\scripts
.\.venv\Scripts\Activate.ps1
python render_excalidraw.py ..\..\..\..\artifacts\diagrams\my-diagram.excalidraw
```

Output PNG is written next to source `.excalidraw` file.

### Fallback: no Python and no uv

Skip PNG generation. Create the standalone `.html` preview and mention that PNG export requires Python/uv or manual export from Excalidraw.

## Local Excalidraw editor commands

Requires Python. If Python is unavailable, create standalone HTML fallback and tell user they can also upload/open the `.excalidraw` file at <https://excalidraw.com>.

With uv:

macOS/Linux shell:

```bash
cd .claude/skills/excalidraw-diagram/scripts && uv run python export_to_excalidraw_url.py ../../../../artifacts/diagrams/my-diagram.excalidraw --port 0
```

Windows PowerShell:

```powershell
cd .claude\skills\excalidraw-diagram\scripts; uv run python export_to_excalidraw_url.py ..\..\..\..\artifacts\diagrams\my-diagram.excalidraw --port 0
```

With venv:

macOS/Linux shell:

```bash
cd .claude/skills/excalidraw-diagram/scripts
. .venv/bin/activate
python export_to_excalidraw_url.py ../../../../artifacts/diagrams/my-diagram.excalidraw --port 0
```

Windows PowerShell:

```powershell
cd .claude\skills\excalidraw-diagram\scripts
.\.venv\Scripts\Activate.ps1
python export_to_excalidraw_url.py ..\..\..\..\artifacts\diagrams\my-diagram.excalidraw --port 0
```

Script prints `http://127.0.0.1:<port>`. Open that URL in a browser for visual editing.

## Required references

Read before generating JSON:

- `references/color-palette.md` — single source of truth for colors.
- `references/element-templates.md` — copyable element shapes.
- `references/json-schema.md` — compact schema reference.
- `references/html-preview-template.html` — standalone browser preview template.

Do not invent colors. Use palette semantics.

## Core philosophy

Diagrams should **argue visually**, not merely display labels.

Tests:

- **Isomorphism test**: If text disappeared, would structure still communicate concept?
- **Education test**: Can viewer learn something concrete from visual examples?

## Depth assessment

Before drawing, decide depth:

### Simple / conceptual

Use abstract shapes when:

- Explaining mental model or philosophy.
- Audience does not need implementation details.
- Concept itself is abstraction.

### Comprehensive / technical

Use concrete examples when:

- Diagramming real system, protocol, architecture, API, or workflow.
- Diagram teaches how something actually works.
- Audience needs real formats, names, payloads, or endpoints.

For technical diagrams, research actual specs and include evidence artifacts.

## Technical research mandate

Before drawing technical diagrams:

1. Look up actual JSON/data formats, event names, method names, API endpoints, or config fields.
2. Understand how pieces connect.
3. Use real terminology, not generic placeholders.
4. Include concrete snippets or examples where useful.

Bad: `Protocol → Frontend`

Good: `AG-UI streams RUN_STARTED + STATE_DELTA → frontend handler renders state`

## Evidence artifacts

Evidence artifacts prove accuracy and teach concrete shape of system.

Use relevant types:

| Artifact type | When to use | Rendering style |
| --- | --- | --- |
| Code snippets | APIs, integrations, implementation | `#f1f5f9` rectangle + syntax-colored text (shows dark in dark mode) |
| JSON/data examples | Payloads, schemas, config | `#f1f5f9` rectangle + green text `#15803d` |
| Event sequences | Protocols, lifecycles | Timeline line + dots + labels |
| UI mockups | Visible user output | Nested rectangles mimicking UI |
| Real input content | System input | Rectangle with sample content |
| API/method names | Interfaces | Actual names from docs |

## Multi-zoom architecture

Comprehensive diagrams should show:

1. **Summary flow** — pipeline at glance.
2. **Section boundaries** — grouped regions.
3. **Detail inside sections** — evidence artifacts and concrete examples.

## Container discipline

Default to free-floating text. Use containers only when shape carries meaning or grouping is needed.

Aim for less than 30% of text inside containers.

Use container when:

- Focal point of section.
- Visual grouping needed.
- Arrows connect to it.
- Shape itself carries meaning.

Use free-floating text when:

- Label, annotation, metadata, section title.
- Typography alone creates hierarchy.

## Design process

Do this before JSON:

1. **Assess depth** — simple/conceptual or comprehensive/technical.
2. **Research if technical** — actual specs, names, formats.
3. **Understand concepts** — what each concept does, relationships, transformation, what viewer must see.
4. **Map concepts to visual patterns**.
5. **Sketch eye flow** — left-to-right, top-to-bottom, radial, or cycle.
6. **Generate JSON** — section by section for large diagrams.
7. **Preview and validate** — use HTML preview first; PNG if available.

## Pattern library

| Concept behavior | Use pattern |
| --- | --- |
| Spawns multiple outputs | Fan-out, radial arrows from center |
| Combines inputs | Convergence/funnel |
| Has hierarchy | Tree lines + free-floating labels |
| Is sequence | Timeline line + dots |
| Loops/improves | Cycle/spiral |
| Is fuzzy context | Overlapping ellipses/cloud |
| Transforms input to output | Assembly line |
| Compares | Side-by-side contrast |
| Separates phases | Visual gap or divider |

Each major concept in multi-concept diagram should use distinct visual pattern.

## Shape meaning

| Concept type | Shape |
| --- | --- |
| Labels/descriptions/details | Text only |
| Section titles/annotations | Text only |
| Timeline markers/bullets | Small ellipse |
| Start/trigger/input | Ellipse |
| End/output/result | Ellipse |
| Decision/condition | Diamond |
| Process/action/step | Rectangle |
| Abstract state/context | Overlapping ellipses |

## Style rules

- `roughness: 0` for clean technical diagrams.
- `opacity: 100` for all elements.
- `strokeWidth: 1` thin, `2` standard, `3` bold sparingly.
- Use whitespace as hierarchy; important elements get 200px+ breathing room.
- Connections required: if A relates to B, add arrow or structural line.
- Text `fontFamily: 3`.
- Text `text` and `originalText` contain readable words only.
- Use `appState.viewBackgroundColor: "#ffffff"` and `appState.theme: "dark"`. Diagrams open in dark mode; Excalidraw darkens the palette on screen (`invert(93%) hue-rotate(180deg)`), so keep authoring with the light palette colors. The renderer and HTML preview apply the same filter. Use `"theme": "light"` only when the user asks for a light diagram.

Base JSON:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [],
  "appState": {
    "viewBackgroundColor": "#ffffff",
    "theme": "dark",
    "gridSize": 20
  },
  "files": {}
}
```

## Large diagram strategy

Build section-by-section:

1. Create wrapper and first section.
2. Add one section per step.
3. Use descriptive IDs: `intake_rect`, `risk_arrow`, `summary_text`.
4. Namespace seeds by section: `100001`, `200001`, etc.
5. Verify bindings reference existing elements.

Do not write generator scripts for one-off diagrams. Hand-authored JSON is easier to adjust.

## Preview-view-fix loop

Visual validation is required after creating or editing diagram JSON. Prefer Python-based local editor preview when available, but provide standalone HTML fallback when Python is unavailable.

1. Start local Excalidraw editor URL from `scripts/export_to_excalidraw_url.py` when Python is available, then open it in a browser.
2. If Python is unavailable, create or update standalone `.html` fallback from `references/html-preview-template.html`.
3. If Python/uv is available, also render `.excalidraw` to `.png`.
4. View local editor URL, standalone HTML fallback, or PNG preview.
5. Audit concept:
   - Structure matches intended argument?
   - Eye flows in designed order?
   - Visual hierarchy clear?
6. Audit defects:
   - Text clipped or overflowing.
   - Text/shapes overlap.
   - Arrows cross through elements unnecessarily.
   - Arrows land on wrong targets or empty space.
   - Labels float ambiguously.
   - Spacing uneven.
   - Text too small.
   - Composition lopsided.
7. Fix JSON.
8. Re-preview.
9. Repeat until diagram can be shown without caveats.

## Quality checklist

- Technical research done when needed.
- Evidence artifacts included for technical diagrams.
- Multi-zoom structure present for comprehensive diagrams.
- Visual structure mirrors concept behavior.
- Each major concept has suitable pattern.
- No uniform card grid unless grid itself is point.
- Minimal containers; typography carries labels.
- Every relationship has arrow/line.
- Text readable and unclipped.
- Arrows connect to intended elements.
- Spacing balanced.
- Standalone HTML fallback created and inspected when Python is unavailable or user requests downloadable preview.
- PNG rendered when local runtime exists.

## Final response

Mention exact workspace-relative paths:

- `artifacts/diagrams/<name>.excalidraw` (source)
- `artifacts/diagrams/<name>.html`
- `artifacts/diagrams/<name>.png` if generated

If editor server started, include local URL.
