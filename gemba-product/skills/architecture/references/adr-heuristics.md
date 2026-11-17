# ADR heuristics

A fixed list of questions to review a set of ADRs before accepting them. Pass every ADR of the set through every row, then pass the whole set through them once more. A heuristic only finds a gap or a contradiction; it decides nothing by itself.

| Heuristic | Question | Skip when |
| --- | --- | --- |
| Browser and server boundary | What runs in the browser and what runs on the server, and where do the data and the secrets live? Does any decision put a secret, a private rule or a private datum where the person who uses the product can read it? | No decision of the set splits work between a client and a server |
| Gaps between ADRs | Does a story of the current release or a constraint of the brief need something that no ADR of the set decides, including what ties two decisions together (who calls whom, what runs on a schedule, who signs in)? | Every story and every constraint already has the decision it needs |
| Limited resource | Does a decision depend on a quota or a limit (storage, requests, messages, a free plan), and does the volume of the brief fit inside it with its source cited? | No decision depends on a quota or a limit |
| Contradictions | Does an ADR say something that another ADR of the set, or an ADR already accepted in the space, denies, or assume what another one rules out? | The set has a single ADR and the space has no accepted ADR |

## Where each finding lands

A finding ends in exactly one of two places:

- A question to the person, for everything the brief, the Story Map and the ADRs do not decide.
- A new ADR, only when a story of the release or a constraint of the brief already decides it, as section 4 of `SKILL.md` requires.

A finding rests on something the brief, the Story Map or an ADR states, never on what a product of this kind usually needs, and a single ADR with nothing that contradicts or leaves out what those sources state has no finding.

Never invent a decision to close a gap.
