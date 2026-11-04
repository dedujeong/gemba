---
type: llm
focus: trace
---
The person asks for the spec JSON of the architecture diagrams of a product. No Confluence connection exists, so Claude writes the spec in the reply. Only the spec Claude writes is judged, never the person's message, which says things the diagrams must not repeat.
The title of a deployment boundary (a section) names only the platform where its pieces run, never its plan, such as "Static hosting provider", and the one short line under a diagram heading says what the diagram shows: neither counts as a description of a box. A table or text that Claude writes outside the JSON spec is not part of a diagram either.
PASS if, in the JSON spec Claude writes, every box (the product, each external system and each container) is only a name, with no "description" or technology field or text, there is no legend or note, and every arrow label (in Context, Containers, the data model and the states) is a short intention that starts with a capital letter.
FAIL if any box in the spec has a description or a technology, if the spec has a legend or a note, or if any arrow label starts with a lowercase letter or explains more than the intention.
