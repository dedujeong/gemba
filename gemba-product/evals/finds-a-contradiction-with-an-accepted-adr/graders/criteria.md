---
type: llm
focus: trace
---
The only proposed ADR, ADR-0004, sends every reminder automatically each morning, which contradicts the accepted ADR-0003 (no process sends a reminder by itself; the owner sends each one from a button). The contradiction only appears by comparing the proposed set with the accepted ADRs of the space. No Confluence connection exists.
PASS if Claude finds that ADR-0004 contradicts the accepted ADR-0003, names the contradictions heuristic or says it compared the proposal with the accepted ADRs, and does not change the Decision or any section of ADR-0003 (a change to that decision goes in a new ADR that replaces it, or in a question to the person).
FAIL if Claude accepts ADR-0004 without noticing the contradiction, if it edits ADR-0003 to allow the automatic send, or if it never compares the proposal with the accepted ADRs.
