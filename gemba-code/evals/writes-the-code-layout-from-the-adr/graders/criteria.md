---
type: llm
---
The project has no CLAUDE.md. The person gives an accepted ADR of the code layout. The session cannot write files, so the CLAUDE.md is expected as content in the response. The ADR says:

- Folders: `src/lib/business`, `src/lib/menu` and `src/lib/order`, each with `components`, `services`, `types.ts` and `index.ts`, and `src/lib/shared` with `ui`, `supabase` and `r2`; the routes `(public)/[business]`, `(auth)/login` and `(admin)/dashboard`.
- Tests: unit tests with Vitest next to each file with the same name (`business.server.test.ts`); end to end tests with Playwright in `tests/e2e` at the repository root.
- File names: kebab-case, and Svelte components in PascalCase.
- Migrations: `supabase/migrations` at the repository root.

PASS if the CLAUDE.md in the response has a section named Code layout that covers the folders, the tests, the file names and the migrations, with the values of the ADR.
FAIL if there is no Code layout section, if one of the four is missing, or if a value contradicts the ADR.
