# Gemba Product

Product discovery for Claude: from an idea or a client request to a Product Brief with labeled evidence and a Story Map with a closed MVP, in Confluence.

You tell the idea in your own words. Claude asks one round of questions about what has actually happened, writes the brief and keeps it current as evidence arrives, then builds the Story Map with you until you close the MVP. Before a client meeting, it drafts an interview kit from what the brief still does not know. The closed Story Map ends discovery and is where development starts.

## Install

```bash
/plugin marketplace add dedujeong/gemba
/plugin install gemba-product@gemba
```

## Requirements

- Claude or Claude Code.
- The Atlassian connector, with access to the product's Confluence space.

## Skills

Each step rests on a method, named here so you know what it is based on before you use it.

- `pitch` hears the idea and writes the Product Brief. Its primary job is a Jobs to be Done statement: when a situation happens, what the person wants and the outcome they are after.
- `interview-kit` prepares the client meeting from what the brief still does not know. Every question asks about past facts, the last time something happened, never opinions or hypotheticals.
- `story-map` turns the brief into scope and closes the MVP. It follows Jeff Patton's User Story Mapping: activities, the tasks inside them and a release cut across the stories.
- `architecture` decides the architecture once the MVP is closed. Each decision is recorded as an ADR, accepted or replaced but never edited, and the system is drawn as C4 diagrams.

## Conventions

- One Confluence space per product.
- Every fact in the brief carries its source: interview, secondhand or assumption.
- No version numbers in titles or documents; Confluence keeps the history.
- Conversation in your language; headings and labels in English.
