# Confluence whiteboard SVG

What the Atlassian connector accepts and returns for whiteboards, learned by probing it. The format guide that `getContentFormatGuide` serves for whiteboards is general; this file records what matters for the Story Map.

## Reading

`getConfluenceContent` with `content_format: svg` (or `png` for a screenshot URL). Do not pass `detail`; whiteboards reject it. The SVG comes back with a line number at the start of each line.

## Elements

- **Sticky:** `<rect data-type="sticky" id width="240.05" height="144.03" x y fill>` plus a `<text belongs-to="ID">` with one `<tspan>` holding the text. Confluence normalizes fills to its palette (for example `#ffefae` becomes `#fce4a6`).
- **Free text:** `<text data-type="text" x y width font-scale>` with tspans. Row labels use a blank tspan, a bold 27px title tspan, and a 15.47px description tspan; a reader finds the rows by that bold 27px title.
- **Mentions:** a `<tspan data-mention-id>` sent through the API is stored as plain text, with or without `data-access-level`. Only mentions made in the UI work, so the generated board names no people.
- **Font sizes:** tspans keep only `15.47px` and `27px`; any other size becomes `15.47px`. Use `font-scale` on the `<text>` to enlarge.
- **Card:** `<rect data-type="card">` plus its text. Avoid; open questions belong in the brief, not on the board.

## Colors

Colors used by `build_story_map.py` (meanings in `SKILL.md`). Confluence may snap a fill to the nearest color in its palette, so these are the values it stores:

| Row | Fill |
|---|---|
| User persona | `#eed7fc` |
| Activities | `#baf3db` |
| Tasks | `#cfe1fd` |
| Current release stories | `#fce4a6` (orange) |
| Later releases | `#f0f1f2` (gray) |
| Open decision | `#ffd5d2` (red) |

Probed snapping: `#fedec8` and `#fff3eb` become the light red `#ffeceb`; `#ffe2bd` and `#f8e6a0` become orange `#fce4a6`; `#fec195` becomes red `#ffb8b2`; `#dcdfe4` becomes `#f0f1f2`. Yellow is a different family (`#fef7c8`, `#f5e989`).

## Creating

`createConfluenceContent` with `contentType: whiteboard`, `parent: {spaceId, parentContentId?}`, `title: "Story Map"`, `body: {format: "svg", value: <full SVG>}`.

Positions on import:

- The whole board is translated; only relative positions matter.
- A free text's `y` is read as its vertical center and stored as its top. A row label with a one-line description is about 102 units tall at scale 1, plus about 22 per extra line (about 42 characters per line at width 344). `build_story_map.py` adds half the estimated height so labels land where intended.
- A separate large title is pushed up so its top stays about 113 units above the text below it, which leaves a visible gap. The product name and the vision therefore share one text element, like the row labels.
