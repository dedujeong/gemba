# Estimation

The original estimate is the hours one person needs to take the issue from its branch to Done while working with Claude: plan, tests, code, review and merge. It is the base metric, with no factor on top. Calibration comes later, from comparing it with the worklogs; never adjust an estimate here by past results, team size or a correction factor.

| Work type | Original estimate |
| --- | --- |
| Story, Task, Bug | The expected hours, in whole hours (`1h`, `2h`, `3h`) |
| Spike | Its timebox in hours, exactly as the maintainer sets it. If they did not set one, propose it and say it is the timebox |
| Epic | None: it is done through its children |

## Reference

Use the closest row as an anchor, then adjust for what this issue adds or removes.

| Hours | What it usually is |
| --- | --- |
| 1h | A change in one place that an existing test pattern already covers: a rule, a field, a fix with its reproducing test |
| 2h | A new behavior with a few acceptance criteria in one part of the code, tests included |
| 3h to 4h | A behavior that crosses two or three parts (for example a screen, its data and a permission), or a first piece of a new area |
| 6h to 8h | A new area with its setup: a new integration, a new kind of document or flow, with its tests |

An issue estimated above 8h is too big for one issue: propose splitting it into Stories or Tasks of 8h or less, each with its own criteria.

## Proposing it

- Propose the estimate with the declaration, so the maintainer reviews it before anything is created.
- If the maintainer gives or changes an estimate, use their value as it is: no rounding, no factor.
- Send it in the create call as `timetracking: {"originalEstimate": "<n>h"}`.
