# Confluence whiteboard SVG

What the Atlassian connector accepts and returns for whiteboards, learned by probing it. The format guide that `getContentFormatGuide` serves for whiteboards is general; this file records what matters for the Story Map.

## Reading

`getConfluenceContent` with `content_format: svg` (or `png` for a screenshot URL). Do not pass `detail`; whiteboards reject it. The SVG comes back with a line number at the start of each line.

## Elements

- **Sticky:** `<rect data-type="sticky" id width="240.05" height="144.03" x y fill>` plus a `<text belongs-to="ID">` with one `<tspan>` holding the text. Confluence normalizes fills to its palette (for example `#ffefae` becomes `#fce4a6`; see Colors).
- **Free text:** `<text data-type="text" x y width font-scale>` with tspans. Row labels use a blank tspan, a bold 27px title tspan, and a 15.47px description tspan; a reader finds the rows by that bold 27px title.
- **Mentions:** a `<tspan data-mention-id>` sent through the API is stored as plain text, with or without `data-access-level`. Only mentions made in the UI work, so the generated board names no people.
- **Font sizes:** tspans keep only `15.47px` and `27px`; any other size becomes `15.47px`. Use `font-scale` on the `<text>` to enlarge.
- **Card:** `<rect data-type="card">` plus its text. Avoid; open questions belong in the brief, not on the board.

## Colors

Colors used by `build_story_map.py` (meanings in `SKILL.md`). The sticky palette of Confluence is closed, 30 values; a fill outside it is snapped to the nearest one and the stored color changes, so always send an exact value:

| Row | Fill |
|---|---|
| User persona | `#f5e989` (yellow) |
| Activities | `#eed7fc` (purple) |
| Tasks | `#cfe1fd` (blue) |
| Current release stories | `#baf3db` (green) |
| Next release stories | `#fce4a6` (orange) |
| Later releases | `#fff5db` (light orange) |
| Delivered releases | `#f0f1f2` (gray) |
| Open decision | `#ffd5d2` (red) |

The palette, light / medium / strong:

| Hue | Light | Medium | Strong |
|---|---|---|---|
| Blue | `#e9f2fe` | `#cfe1fd` | `#adcbfb` |
| Teal | `#e7f9ff` | `#c6edfb` | `#b1e4f7` |
| Green | `#dcfff1` | `#baf3db` | `#97edc9` |
| Lime | `#efffd6` | `#d3f1a7` | `#bde97c` |
| Yellow | `#fef7c8` | `#f5e989` | `#efdd4e` |
| Orange | `#fff5db` | `#fce4a6` | `#fbd779` |
| Red | `#ffeceb` | `#ffd5d2` | `#ffb8b2` |
| Magenta | `#ffecf8` | `#fdd0ec` | `#fcb6e1` |
| Purple | `#f8eefe` | `#eed7fc` | `#e3bdfa` |
| Gray | `#ffffff` | `#f0f1f2` | `#b7b9be` |

Probed snapping: `#fedec8` and `#fff3eb` become the light red `#ffeceb`; `#ffe2bd` and `#f8e6a0` become orange `#fce4a6`; `#fec195` becomes red `#ffb8b2`; `#dcdfe4` becomes `#f0f1f2`. `read_story_map.py` takes both reds (`#ffd5d2`, `#ffeceb`) as an open question.

## Creating

`createConfluenceContent` with `contentType: whiteboard`, `parent: {spaceId, parentContentId?}`, `title: "Story Map"`, `body: {format: "svg", value: <full SVG>}`.

Positions on import:

- The whole board is translated; only relative positions matter.
- A free text's `y` is read as its vertical center and stored as its top. A row label with a one-line description is about 102 units tall at scale 1, plus about 22 per extra line (about 42 characters per line at width 344). `build_story_map.py` adds half the estimated height so labels land where intended.
- A separate large title is pushed up so its top stays about 113 units above the text below it, which leaves a visible gap. The product name and the vision therefore share one text element, like the row labels.

## Patching

`updateConfluenceContent` with `contentId`, `body: {format: "svg", value: PATCH, context: {content: <exact SVG from the last read, with line numbers>}}`. A `title` parameter renames the board.

Patch operations:

- `<delete_svg from="N" to="M"/>`: both attributes are required.
- `<replace_svg from="N" to="M">...</replace_svg>`: replace whole `<text>` or `<rect>` elements; a bare `<tspan>` is invalid.
- `<insert_svg line="N">...</insert_svg>`: new elements get new ids.

What a patch keeps, tested on a board the person had arranged by hand:

- Stickies the person moved stay where they are when another sticky is replaced or inserted. Read the board right before the patch and use that read as `context`.
- Replacing a free text (title or row label) moves it, even with the coordinates it was read with: its `y` is taken as a vertical center again (a label moved 10.58 units up). Change free texts in the interface, not through the API.
- Creating the board again does not update it: it makes a second board and drops the layout.

Not tested: a patch with a stale read, and deleting stickies.
