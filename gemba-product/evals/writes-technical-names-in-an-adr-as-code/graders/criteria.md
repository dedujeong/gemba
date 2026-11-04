---
type: llm
focus: trace
---
The person accepted an ADR whose decision names technical things: the table `bookings`, the columns `starts_at` and `student_id`, the folder `db/migrations`, the file `supabase/config.toml`, the domain `reservas.estudio-yoga.mx`, the folder `dist` and the command `supabase db push`. No Confluence connection exists, so Claude drafts the page in the reply. The names also appear, as plain text, in the person's own message, which does not count: only the ADR Claude drafts is judged, and only its body, never its title, because a page title cannot carry code style.
PASS if, in the ADR Claude drafts, every one of those technical names is written with code style (inside backticks, or a code tag), wherever it appears in the body (Context, Decision, Alternatives, Consequences and Source).
FAIL if any of them appears in the body of the ADR as plain text.
