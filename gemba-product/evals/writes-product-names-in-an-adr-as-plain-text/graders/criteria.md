---
type: llm
focus: trace
---
The person accepted an ADR that names products, providers and tools: Supabase, Postgres, Cloudflare Pages, GitHub, Firebase, Firestore and Vercel Hobby. Next to them it names technical things: `supabase/config.toml`, `supabase db push` and `dist`. No Confluence connection exists, so Claude drafts the page in the reply. The names also appear in the person's own message, which does not count: only the body of the ADR Claude drafts is judged, never its title.
A technical name that contains the name of a tool, such as `supabase db push` or `supabase/config.toml`, is code as a whole and is never a violation. Only a bare product, provider or tool name, like Supabase on its own, must be plain text.
PASS if, in the body of the ADR Claude drafts, every product, provider and tool name is plain text, with no backticks and no code tag, while the technical names `supabase/config.toml`, `supabase db push` and `dist` keep code style.
FAIL if any product, provider or tool name is written with code style in the body, or if a technical name is left as plain text.
