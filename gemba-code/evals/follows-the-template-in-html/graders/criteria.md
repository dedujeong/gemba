---
type: llm
---
The maintainer asks for a technical Task. The Task template is an opening paragraph with no heading (what it enables and why it exists) followed by an H3 section "Done when" with a bulleted list of verifiable results.

PASS if the drafted Task's description has that shape (an opening paragraph without heading, then a "Done when" heading with bullets, section headings in English, content in Spanish) and it is written as HTML (for example `<p>`, `<h3>`, `<ul><li>`), or the drafted create call sends it with an HTML content format.
FAIL if the description lacks the opening paragraph or the "Done when" section, adds sections the template does not have, is written only as Markdown, or no declaration is drafted.
