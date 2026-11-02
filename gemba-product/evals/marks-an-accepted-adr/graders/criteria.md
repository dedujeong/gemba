---
type: llm
focus: trace
---
The person accepts a decision ADR that was a Rough draft, exactly as written. No Confluence connection exists, so Claude says in the reply what changes in the page.
PASS if Claude marks the ADR as accepted by moving its page status to Verified and adding a success panel, and it leaves the Context, Decision, Alternatives, Consequences and Source text as they were.
FAIL if the ADR is not marked as accepted, if the status stays Rough draft or becomes another status, if the marking is only a line of text in the body instead of the page status, or if any of the five sections is rewritten.
