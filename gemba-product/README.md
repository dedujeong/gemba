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

## Conventions

- One Confluence space per product.
- Every fact in the brief carries its source: interview, secondhand or assumption.
- No version numbers in titles or documents; Confluence keeps the history.
- Conversation in your language; headings and labels in English.
