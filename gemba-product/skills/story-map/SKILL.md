---
name: story-map
description: Turn the Product Brief into a user story map on a Confluence whiteboard, review that map with the person and close the MVP when they say so. Use when the brief has a clear problem, primary job and enough evidence, or when someone asks for the story map, the MVP or the scope, or when a map already built is being reviewed, counted, changed or closed, or when a release has shipped and is reviewed to prepare the next one. Reads the brief, drafts the map with the MVP cut, builds the whiteboard in the product's space and links it from the brief, then recounts and edits the board during the review.
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

Colors follow the Jira work items and always carry the same meaning, on every board:

| Color | Meaning |
|---|---|
| Yellow | User persona |
| Purple | Activities |
| Blue | Tasks |
| Green | Stories in the current release (the MVP until it ships) |
| Orange | Stories in the next release |
| Light orange | Stories in later releases, and always the Later row |
| Gray | Stories in releases already delivered |
| Red | Unresolved question that blocks a story |

When the MVP ships, mark it `"released": true` in the spec: it turns gray, the next release becomes the current one and turns green, and the rest move up one place.

## 3. Build the whiteboard

Fill `assets/story-map-template.json` with the product's content. Each MVP story carries `traces`, the part of the brief it serves. Then run:

```
python3 scripts/build_story_map.py spec.json story-map.svg
```

The script rejects a story of the current release without `traces`, and prints the count per release and the origin of each MVP story.

Create the board with `createConfluenceContent` (`contentType: whiteboard`, `body.format: svg`, the generated SVG) in the product's space, titled `Story Map`. Then add the sentence "El alcance está en el Story Map." (in the person's language) with the board link to the second paragraph of the brief's Source panel, before its closing sentence. Edit the brief in place with granular edits and keep everything that was already there.

The board header is the product name with a one- or two-sentence `vision` below it: what the product will be and for whom, taken from the brief's Problem and Primary job. It is not a status line, and it names no people: whiteboards drop @mentions created through the API.

If there is no Confluence connection, write the spec in the reply and say that nothing was published.

Details on the whiteboard SVG format are in `references/whiteboard.md`.

## 4. Review the map with the person

The map is conversation material. Reviewing it brings up rules, roles and permissions that the questions did not.

Before citing any number, recount from the board at that moment, never from memory or from what was said earlier. Read the board with `getConfluenceContent` (`content_format: svg`), save the SVG to a file and run:

```
python3 scripts/read_story_map.py board.svg --previous <stories the current release had when last reported>
```

It prints the stories and open questions per release, the stories of each task, and whether the current release grew, shrank or stayed the same. A gray release is read as delivered and is not part of the current release's scope; the current release is the first one that is not delivered (the MVP until it ships). An open question (red sticky) is not a story. `--json` gives the personas and, per release, each task with its activity and stories.

When the MVP grew, say by how much and recommend which stories move to the next release, naming them. Start with the ones that trace to no Quality bar condition and that a manual step covers. The person decides.

## 5. Change the map without undoing the person's layout

The person may arrange the board by hand. Changing its content must keep that layout:

- Change only stickies, with `updateConfluenceContent` and patch operations (`replace_svg`, `insert_svg`), and read the board right before each patch so the patch carries the positions the person left.
- The row labels (User persona, Activities, Tasks, each release and Later) are changed through the API too, with `scripts/label_story_map.py`, and the person is asked for no step in the interface. The board header (product name and vision) is the one free text Claude does not replace: Confluence moves it, so the person changes it in the interface.
- Do not recreate the board. Creating it again would drop the layout and leave a second board.

Details are in `references/whiteboard.md`.

### Change or add a row label

When the scope of a release changes, its label changes with it. The script changes the text under the title, not the title itself; renaming a row is a change for the interface. Change the stickies first, then read the board again, because the label goes level with the top of the first row of stickies of its release as the board is now:

1. Read the board with `getConfluenceContent` (`content_format: svg`) and save the SVG.
2. To change the text of a label: `python3 scripts/label_story_map.py board.svg --label "<row name>" --description "<new text>"`. Without `--description` it only realigns the label. For a row without stickies, add `--top <y>`.
3. To add the label of a new release or of the Later row: `python3 scripts/label_story_map.py board.svg --add "<name>" --description "<text>" --top <y of its first row>`.
4. Send the patch it prints with `updateConfluenceContent`, with the SVG you read in step 1 as `context.content`, whole and with its line numbers.
5. Read the board again: the label sits at the top of its row and nothing else moved. Recount with `read_story_map.py` if stickies changed.

### Recolor a board made with the old colors

When the person asks to update a board to the current colors, change only the fill of each sticky, so no text or position moves:

1. Ask which releases are already delivered. The old gray cannot tell them from later releases, so never guess.
2. Read the board with `getConfluenceContent` (`content_format: svg`), save the SVG and run `python3 scripts/read_story_map.py board.svg` to note the count per release.
3. Run `python3 scripts/recolor_story_map.py board.svg --released "<delivered release>"` (repeat the option for each one). It prints, per color, the ids of the stickies that change.
4. Apply one `update_elements_svg` per color with `updateConfluenceContent`: `ids="<ids>"` and `<attr fill="<color>"/>`.
5. Read the board again and run `read_story_map.py` once more: the count per release must be the same as in step 2.

## 6. Close the MVP

Only the discovery lead closes the MVP, and only by saying so explicitly. "It looks complete", "it's fine" or the end of the review are not a closing: the MVP stays open, nothing is recorded and the page status does not change. Ask once whether they close it, and leave it to them.

When they close it:

- Recount the MVP stories from the board right then (section 4), not from memory.
- In the brief's Open decisions, add a checked item that records the closing with its date as a date node and the number of MVP stories, for example "MVP cerrado el <date node> con 12 historias." Edit the brief in place with granular edits and keep everything else.
- Set the brief's page status to Verified, as `pitch` section 6 describes.
- Tell the person that the discovery is complete: the Story Map, once closed, ends it.

If there is no Confluence connection, write the item and the status in the reply and say that nothing was published.

## 7. Review a closed release and prepare the next one

When a release has shipped and the person asks to review it, the facts of what was delivered come from Jira, not from the board; the board is only touched for what was not delivered. The stories of the map are 1:1 with the Stories of Jira.

1. **What was delivered.** Search the Stories of the release's fix version with `searchJiraIssuesUsingJql` and ask for status, original estimate and time spent. Show which Stories are Done and which are not, and the time spent against the original estimate, per Story and in total. Add the times with a tool (Bash), never from memory, and say when a Story has no estimate.
2. **What the board says.** Read the board (section 4). A gray release is delivered: it is read as delivered and does not count in the scope of the next one. The current release is the first one that is not delivered; Later is never the current release.
3. **What was not delivered.** For each such Story, read its description and propose the sticky it matches (same task, same release). If no sticky is clear, say so; never guess. Ask the person where each one goes: the next release or Later. Nothing moves before they answer.
4. **Apply what the person decides,** reading the board again before each patch and sending each patch with `updateConfluenceContent` and that read as `context.content`, whole:
   - Move the stories: `python3 scripts/move_story_map.py board.svg --story <sticky id> --to "<release or Later>"` (each story carries its sticky `id` in `read_story_map.py --json`; one run per destination; only stories move, not personas, activities or tasks). If a row gets deeper, the rows below move down with it.
   - Read the board again and recolor it: `python3 scripts/recolor_story_map.py board.svg --released "<delivered release>"`, naming every delivered release, the ones already gray included, and the one just reviewed once the person confirms it as delivered. Then the next release is green and the rest move up (section 5, Recolor).
   - If the scope of a release changed, update its label (section 5, Change or add a row label).
5. **Recount** from the board with `read_story_map.py` before citing any number (section 4), and tell the person which release is now the current one and how many stories it has.

The person decides what moves and when a release counts as delivered. Claude proposes and checks that the board agrees.
