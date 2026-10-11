# Color Palette & Brand Style

Single source of truth for diagram colors. Edit this file to customize brand style.

## Shape colors

Colors encode meaning, not decoration.

| Semantic purpose | Fill | Stroke |
| --- | --- | --- |
| Primary/Neutral | `#3b82f6` | `#1e3a5f` |
| Secondary | `#60a5fa` | `#1e3a5f` |
| Tertiary | `#93c5fd` | `#1e3a5f` |
| Start/Trigger | `#fed7aa` | `#c2410c` |
| End/Success | `#a7f3d0` | `#047857` |
| Warning/Reset | `#fee2e2` | `#dc2626` |
| Decision | `#fef3c7` | `#b45309` |
| AI/LLM | `#ddd6fe` | `#6d28d9` |
| Inactive/Disabled | `#dbeafe` | `#1e40af` plus dashed stroke |
| Error | `#fecaca` | `#b91c1c` |

Always pair darker stroke with lighter fill.

## Text colors

| Level | Color | Use for |
| --- | --- | --- |
| Title | `#1e40af` | Section headings, major labels |
| Subtitle | `#3b82f6` | Subheadings, secondary labels |
| Body/Detail | `#64748b` | Descriptions, annotations, metadata |
| On light fills | `#374151` | Text inside light-colored shapes |
| On dark fills | `#ffffff` | Text inside dark-colored shapes |

## Evidence artifact colors

| Artifact | Background | Text color |
| --- | --- | --- |
| Code snippet | `#f1f5f9` | `#1e293b`, syntax-colored where practical |
| JSON/data example | `#f1f5f9` | `#15803d` |

Dark mode inverts these: the light block shows near-black with light text, like a code editor.

## Default lines

| Element | Color |
| --- | --- |
| Arrows | Source element stroke color |
| Structural lines | `#1e3a5f` or `#64748b` |
| Marker dots | `#3b82f6` fill and stroke |

## Background

Canvas background: `#ffffff`, shown dark: scenes set `appState.theme: "dark"` and Excalidraw inverts the palette on screen. Pick colors from this light palette; do not hand-pick dark colors.
