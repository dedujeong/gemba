---
type: llm
---
The maintainer declared the version `Taller v0.2.0` and asks to put the keys on the Story Map. The current release, Release 2, has three story stickies: "Save the vehicle" (TALLER-31), "Suggest the date by service type" (TALLER-32) and "Remind the day before" (TALLER-33).

There is no connection to Confluence in this session, so the response only writes the calls it would make. Saying that nothing was written is expected: a key is written when its patch is drafted.

PASS if the response drafts a patch for the board (a `replace_svg` per sticky, or the output of running the skill's script) in which each of the three story stickies keeps its story text and gains its own key as a last line of the sticky, under the text: TALLER-31 on "Save the vehicle", TALLER-32 on "Suggest the date by service type" and TALLER-33 on "Remind the day before".
FAIL if a story sticky is left without its key, if a key goes on another sticky, if the story text is changed, replaced or deleted, or if no patch for the board is drafted.
