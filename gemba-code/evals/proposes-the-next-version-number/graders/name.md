---
type: llm
---
The maintainer did not give the version number. The product is Taller and its published versions are `Taller v0.1.0` and `Taller v0.1.1`. The next release raises the minor number and a fix version is named `<Product> vX.Y.Z`.

Judge the version number Claude proposes for the fix version, and whether it asks for the number.

PASS if the fix version Claude proposes or drafts is exactly `Taller v0.2.0`, and Claude does not ask the maintainer for the number (it may ask them to confirm or change the proposed one).
FAIL if the proposed name is anything else, if no number is proposed, or if Claude asks the maintainer which number the version has.
