# Architecture diagrams

Which diagram to draw, where it lives, and what the Confluence whiteboard does with it. The rules below were learned by building a board by hand and reading it back, so they are what the connector stores, not what its format guide suggests.

## Which levels

C4 levels, by where they belong:

| Level | When | Where |
|---|---|---|
| Context | Always | Architecture page |
| Containers | More than one deployable piece | Architecture page |
| Data model | The stories name entities the product keeps | Architecture page |
| States of an entity | An entity of the data model changes state | Architecture page, one diagram per entity |
| Deployment, sequence | Only when an ADR needs it | Inside that ADR |
| Components | During development | Gemba Code, aligned with the Jira components |
| Code | Never | |

A product with one deployable piece gets Context alone: a Containers diagram with a single box says nothing the Context diagram does not.

## What each shape means

| Element | How it is drawn | Why |
|---|---|---|
| A role that uses the product | A 124x124 rectangle, fill `#cfe1fd`, with its name as free text underneath | `data-shape="user"` renders square, so a person is a plain rectangle with a label |
| The product, or one of its pieces | A 220x160 `process` shape, fill `#cfe1fd`, stroke `#1558bc` | |
| A store | The same, with `data-shape="database"` | |
| A system somebody else runs | The same, fill `#f0f1f2`, stroke `#7d818a` | Gray says the team does not operate it. What the team operates is never gray and never an external of the Context: it only appears in Containers |
| An entity of the data model | The same 220x160 `process` shape, with its name followed by its main fields in one run of text | The fields come from what the stories name; an entity with no fields is not drawn |
| A state of an entity | The same `process` shape, with only its name | |
| The start of a state diagram | A 40x40 gray rectangle, with an arrow to the first state labelled with the event that creates the entity | |
| A deployment boundary | A `section` rect with `data-title`, its pieces carrying `belongs-to` | The title names the plan it runs on |
| An arrow | A `polyline` with `data-type="connector"`, `begins-at`, `ends-at`, the two anchors at proportion `0.5`, `line-type="angled"` and `marker-end` | |
| What flows along an arrow | A `pathLabel` text bound to the connector with `belongs-to` | |

A box of the Context and Containers diagrams says only its name: no description, no technology. Several `tspan` inside one shape read as a single line, so an entity of the data model, which does carry its fields, writes them in one run of text after its name, not stacked.

The line under a heading says what the diagram shows, in a few words, and never lists its boxes or their technology. A diagram has no legend and no notes beside it: the heading, the boxes and the arrows say everything, and a doubt goes in as a red sticky, never as a note.

## What the connector does to a board

- The arrowhead needs its own `defs`, `marker` and `polygon`, each with an id.
- Shapes are normalized to fixed sizes and the anchors go back to `0.5`. The routing is recalculated, so a bad route is fixed by replacing the connector with other anchors, never by moving its points.
- `pathLabels` survive only on create. Inserted by a patch they are dropped and the call still answers `ok: true`. A label added later has to be free text, which does not follow its connector.
- One `update_elements_svg` per call: several ids or operations in one patch apply only the first and still answer `ok: true`.
- A `replace_svg` of the whole board moved the x of free texts nobody touched.
- The answer of a patch is stale. Read the board again after writing, and look at the PNG when the layout matters.
- The label of an arrow sits on its line, so the gap between two boxes has to fit it: about 9 units per character of the longest label, or the label covers the arrow and the text of the boxes. The data model and state diagrams leave 300 units. Learned by creating a board with 120 and reading its PNG. The Containers diagram works the gap out from the longest label of the arrows that cross it.
- The main flow is one straight row: in Context the product and the first external system share a row, and in Containers the first actor and the first piece of every boundary do. The arrows of the main flow never bend.
