---
type: llm
---
version-start hands over a Story Map card with two stories, after the maintainer already confirmed the whole version. The card is declared as an Epic with one Story per story as its children.

PASS if the response drafts, in this order, the Epic first and then two Stories, one for "Lista de clientes a avisar hoy" and one for "Aviso por WhatsApp", each Story with the Epic as its parent. The Epic has no component and no original estimate, and its description has a Source section with the Story Map URL (https://example.atlassian.net/wiki/spaces/TALLER/whiteboard/123) as a block card in HTML (`data-type="block-card"`).
FAIL if the Epic is missing or comes after its Stories, if there is not one Story per story, if a Story has no parent, if the Epic has a component or an estimate, if the Source is missing or is not a block card.
