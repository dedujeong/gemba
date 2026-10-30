---
name: story-map
description: Turn the Product Brief into a user story map on a Confluence whiteboard. Use when the brief has a clear problem, primary job and enough evidence, or when someone asks for the story map, the MVP or the scope. Reads the brief, drafts the map with the MVP cut, builds the whiteboard in the product's space and links it from the brief.
---

# Story map

The Story Map (Jeff Patton's User Story Mapping) turns the brief into scope. It is the last artifact of discovery.

## 1. Read the brief

Read the `Product Brief` from the product's space. Take actors from Actors and permissions, the flow from Current workflow and Primary job, and constraints from Business rules, Quality bar and Design principles.

## 2. Draft the map

Structure, top to bottom:

- **User persona:** the actors; mark the primary user.
- **Activities:** what happens, in order, from setup to the end of the job. Few and broad.
- **Tasks:** the steps inside each activity, left to right. Each activity sits above its first task.
- **MVP:** the minimum stories that solve the primary job for the primary user. One short sentence each.
- **Release 2** (and later): everything else.

Rules for the MVP cut:

- Every Quality bar condition becomes an MVP story (for example a money calculation or a permission rule). Previous systems often fail on exactly these basics.
- Design principles that change how a task works become stories too.
- Every MVP story says where it comes from in the brief: the Problem, the Primary job or a Quality bar condition. A story that traces to none of them does not belong in the MVP.
- An unresolved question that blocks a story is a red sticky (`"open": true`) and also an item in the brief's Open decisions.
- Prefer a manual step in the MVP over automation; the automated version goes to a later release.

## Colors

Colors always carry the same meaning, on every board:

| Color | Meaning |
|---|---|
| Purple | User persona |
| Green | Activities |
| Blue | Tasks |
| Orange | Stories in the current release (the MVP until it ships) |
| Gray | Stories in later releases |
| Red | Unresolved question that blocks a story |

When the MVP ships, the next release becomes the current one and turns orange.

## 3. Build the whiteboard

Fill `assets/story-map-template.json` with the product's content. Each MVP story carries `traces`, the part of the brief it serves. Then run:

```
python3 scripts/build_story_map.py spec.json story-map.svg
```

The script rejects an MVP story without `traces`, and prints the count per release and the origin of each MVP story.

Create the board with `createConfluenceContent` (`contentType: whiteboard`, `body.format: svg`, the generated SVG) in the product's space, titled `Story Map`. Then add the sentence "El alcance está en el Story Map." (in the person's language) with the board link to the second paragraph of the brief's Source panel, before its closing sentence. Edit the brief in place with granular edits and keep everything that was already there.

The board header is the product name with a one- or two-sentence `vision` below it: what the product will be and for whom, taken from the brief's Problem and Primary job. It is not a status line, and it names no people: whiteboards drop @mentions created through the API.

If there is no Confluence connection, write the spec in the reply and say that nothing was published.

Details on the whiteboard SVG format are in `references/whiteboard.md`.
