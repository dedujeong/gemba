---
type: llm
---
The maintainer confirmed the whole release and asked to create the fix version `Taller v0.2.0` and declare the cards. The current release, Release 2, has two cards: "Record a service", with two stories ("Save the vehicle" and "Suggest the date by service type"), and "Remind", with one story ("Remind the day before"). The Epic's due date is 2026-11-13.

PASS if, after the fix version, the response drafts the declarations in the fix version `Taller v0.2.0`: an Epic for "Record a service" with one child Story per story (each with the Epic as its parent), and for "Remind" a single Story with no Epic and no parent. The Epic carries the due date 2026-11-13, and every issue shows its priority; each Story also shows its component, and the Epic has none. It does not stop to ask the maintainer to approve the declarations before creating them: offering that an estimate can still be changed is not asking.
FAIL if no card is declared, if "Record a service" is not an Epic with its two Stories as children, if "Remind" gets an Epic or a parent, if the Epic lacks the due date or carries a component, if a priority is missing, or if it asks for approval before creating the declarations.
