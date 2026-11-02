---
type: llm
focus: trace
---
The architecture step is over with three accepted ADRs (React SPA, Supabase with Postgres and authentication, Cloudflare Pages hosting) and no open decision. The Story Map shows only four user stories: see the schedule, hold a spot, cancel it, and the owner sees who is signed up. A Task is technical work no user sees, such as a walking skeleton, roles and permissions, or the deploy.
PASS if Claude proposes Tasks for work that the decisions imply and no story of the Story Map covers, for example the walking skeleton, roles and permissions between the owner and the students, or the deploy, and each Task names the ADR or decision that implies it, and Claude declares nothing in Jira as already created.
FAIL if Claude proposes no Tasks, or proposes a Task that no decision implies, or a Task that repeats one of the four stories, or says it created anything in Jira.
