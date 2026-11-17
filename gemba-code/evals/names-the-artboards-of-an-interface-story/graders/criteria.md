---
type: llm
---
The maintainer asks to declare an interface Story, "lista de avisos de hoy". The Design page lists six artboards in total, and assigns only `Notices-Today-Default` and `Notices-Today-Empty` to this Story. The session has no Jira, so the full declaration is expected in the response.

PASS if the description of the drafted Story has an Artboards section that lists `Notices-Today-Default` and `Notices-Today-Empty` and none of the other four artboards, and does not invent an artboard that is not on the page.
FAIL if there is no Artboards section, if it lists an artboard of another story, if it omits one of the two, if it invents a name, or if no declaration is drafted.
