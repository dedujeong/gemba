---
name: writes-the-plan-in-the-project-language
description: In a project whose Language is es-MX, the plan that implement presents is written in Spanish even when the issue and the session context are in English.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Implementa TALLER-21.

The project's CLAUDE.md has this block:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

Session notes: there is no Jira connection, no real git changes and no real plan mode in this session. Follow the flow up to the point where you would enter plan mode. Then write, inside a single fenced block, the exact content of the plan file you would save for plan mode, and nothing after it.

TALLER-21 is a Story in Backlog, with no blockers, in the fix version `Taller v0.1.0`, Summary `Show the phone of each customer in today's list`, component `web`. Acceptance criteria: given a customer in today's list, when the list is shown, then their phone is shown; given a customer with no phone, when the list is shown, then it shows they have none. The walk is done: the screen `src/today/TodayList.tsx` gets the customers from `getTodayCustomers()` in `src/today/customers.ts`, which does not return the phone today, and the screen has no tests.
