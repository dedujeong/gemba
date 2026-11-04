# Criteria heuristics

A fixed list of questions for the cases off the happy path. Pass every acceptance criterion of a Story through every row. A heuristic only finds a gap; it decides nothing by itself.

| Heuristic | Question | Skip when |
| --- | --- | --- |
| Nothing | What happens with no data, empty or at zero? | The criterion receives no data |
| One | Is the case with only one element covered? | The happy path already covers it |
| Many | Is more than one allowed? What happens with the second? | The entity is unique by definition |
| Limit | What happens right at the edge of a value (equal, above, below)? | There is no value with an edge |
| Duplicate | What happens if it already exists or was already done? | The action creates nothing |
| No permission | What happens if someone who should not tries it? | The brief defines no roles for this |
| Half-done failure | What is left if it fails halfway? | The action writes no data |
| Undo | Can it be reverted? Who does it? | The action changes nothing |
| Other state | What happens if it occurs while the entity is in another state? | The entity has no states |

## Where each gap lands

A heuristic that applies to a criterion ends in exactly one of three places:

- A criterion: only when the Product Brief, the Story Map, the card or the maintainer's answer decides the case.
- A line of Out of scope: only when the brief or the Story Map leave it out, in their words.
- A question to the maintainer: everything else.

Never infer a criterion to close a gap.

## Decision table

Use it when a rule depends on two or more conditions (for example payment type and amount against the balance). It is a working tool: build it inside, never in the issue.

1. One column per condition, with its possible values, and one column for the result.
2. Write one row per combination of values.
3. Strike the impossible combinations and say why.
4. Rows with the same result merge into one criterion; each distinct result is one criterion.
5. A row with no known result is a question, not a criterion.
6. The table never goes in the issue and is not shown unless the maintainer asks for it.
