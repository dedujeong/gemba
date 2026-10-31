---
type: llm
---
The maintainer confirmed the release and the version number 0.2.0. The product is Taller. A fix version is named `<Product> vX.Y.Z`.

Judge the name of the fix version Claude creates or drafts (the `name` of the create call, or the name it says the version will have). Other mentions of numbers in the text, such as the previous version or the number on its own, do not count.

PASS if that name is exactly `Taller v0.2.0`.
FAIL if that name is anything else, or no fix version is drafted.
