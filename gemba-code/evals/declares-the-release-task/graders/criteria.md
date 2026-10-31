---
type: llm
---
The maintainer confirmed the whole release and asked to create the fix version `Taller v0.2.0` and declare the cards. The release has an Epic "Record a service" with two Stories and a Story "Remind the day before". The release goes in the component `platform`.

PASS if, after the cards, the response drafts a Task named `Release Taller v0.2.0` in the fix version `Taller v0.2.0`, with the component `platform`, blocked by all the other issues of the version (the Epic and the three Stories), and a "Done when" that lists the version bump, the merge to main, the tag, the GitHub release and the fix version released in Jira.
FAIL if there is no release Task, if it is in another fix version, if it is not blocked by every other issue of the version, or if its Done when lacks any of the five steps.
