---
type: llm
---
The person asks Claude to update the label of the Release 2 row on a Confluence whiteboard, giving the new text ("Registro de vehículos y aviso de la víspera."). In this session there is no Confluence connection, so Claude can only draft the change.

PASS if the response drafts the label change itself: a patch (or the replaced text element) that carries the new text for the Release 2 label, or it runs a script that produces that patch. It must not tell the person to edit the label, or move it, by hand in the Confluence interface.
FAIL if the response asks the person to change the label in the Confluence interface, to move it by hand, or to do any other manual step to finish the change; or if it never drafts the new label text.
