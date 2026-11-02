---
type: llm
focus: trace
---
The decision of ADR-0001 (hosting) changes after it was accepted. ADR-0002 is unrelated. No Confluence connection exists, so Claude says in the reply what is created and what changes.
PASS if Claude creates a new ADR with the next number (ADR-0003) for the new hosting decision that names ADR-0001 as the one it replaces, and leaves the Context, Decision, Alternatives, Consequences and Source of ADR-0001 unchanged (its Decision still says Cloudflare Pages), and does not touch ADR-0002.
FAIL if ADR-0001 is edited to say Vercel Pro or any of its five sections is rewritten, if no new ADR is created, if the new ADR does not say which ADR it replaces, if it reuses the number 0001, or if ADR-0002 is changed.
