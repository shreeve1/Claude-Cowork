# Excalidraw JSON Schema

## Element types

| Type | Use for |
| --- | --- |
| `rectangle` | Processes, actions, components |
| `ellipse` | Entry/exit points, external systems, markers |
| `diamond` | Decisions, conditionals |
| `arrow` | Directed connections |
| `line` | Non-arrow structure |
| `text` | Labels and annotations |
| `frame` | Grouping containers |

## Common properties

| Property | Type | Description |
| --- | --- | --- |
| `id` | string | Unique identifier |
| `type` | string | Element type |
| `x`, `y` | number | Position in pixels |
| `width`, `height` | number | Size in pixels |
| `strokeColor` | string | Border/text color |
| `backgroundColor` | string | Fill color or `transparent` |
| `fillStyle` | string | `solid`, `hachure`, `cross-hatch` |
| `strokeWidth` | number | Usually 1 or 2 |
| `strokeStyle` | string | `solid`, `dashed`, `dotted` |
| `roughness` | number | Use 0 for modern/clean |
| `opacity` | number | Use 100 |
| `seed` | number | Stable random seed |

## Text properties

| Property | Description |
| --- | --- |
| `text` | Display text; readable words only |
| `originalText` | Same as `text` |
| `fontSize` | 16-20 recommended |
| `fontFamily` | Use 3 |
| `textAlign` | `left`, `center`, `right` |
| `verticalAlign` | `top`, `middle`, `bottom` |
| `containerId` | Parent shape id or null |
| `lineHeight` | Usually 1.25 |

## Arrow properties

| Property | Description |
| --- | --- |
| `points` | Array of `[x, y]` coordinates relative to element x/y |
| `startBinding` | Connection to start shape |
| `endBinding` | Connection to end shape |
| `startArrowhead` | null, `arrow`, `bar`, `dot`, `triangle` |
| `endArrowhead` | null, `arrow`, `bar`, `dot`, `triangle` |

Binding format:

```json
{
  "elementId": "shapeId",
  "focus": 0,
  "gap": 2
}
```

Rounded rectangle:

```json
"roundness": {"type": 3}
```
