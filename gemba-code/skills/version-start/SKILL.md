---
name: version-start
description: Open a version from the closed Story Map: read the Product Brief and the current release of the Story Map from Confluence, point out its open questions and have the maintainer confirm each card as a Story or an Epic before anything is declared. Use when someone says "abre la versión", "arranca la versión", "inicia el release", or that discovery closed a release and development starts.
---

# Start a version

You open a version from what discovery agreed. Confluence is the only source: the Product Brief and the Story Map are read from the product's space every time, and no copy of them goes to the repository, in Markdown or any other format.

## 1. Find the project

Read the `## Gemba` section of the project's `CLAUDE.md`: `Jira Project`, `Confluence Space` and `Language`. If it is missing, propose running `setup` first and stop. Get the cloudId once with `getAccessibleAtlassianResources`.

## 2. Read the Product Brief

Find it with `searchConfluence` (`space = "<Confluence Space>" AND title ~ "Product Brief"`) and read it with `getConfluenceContent` (`detail: full`, `content_format: markdown`). If the space has more than one brief, ask which product the version is for. If it has none, say that discovery has to write it first and stop.

## 3. Read the current release of the Story Map

Find the whiteboard with `searchConfluence` (`space = "<Confluence Space>" AND type = whiteboard AND title ~ "Story Map"`), the one of the same product as the brief. Read it with `getConfluenceContent` (`content_format: svg`).

Save the SVG to a temporary file outside the repository (`mktemp`), run `python3 scripts/read_release.py <file>` and delete the file. The script takes the current release, the first one not gray: a gray release was already delivered and does not count. It returns that release's stories by activity and task, and its red stickies as open questions apart.

If every release is gray, say that the Story Map has no release left to open and that discovery has to plan the next one, and stop.

## 4. Point out open questions

Before anything else, point out each open question of the release, in its own words. An open question is not a story and is never declared: while one is open, nothing of the version is declared. Ask the person to resolve it, in discovery or by telling you the decision, and wait.

## 5. Confirm the release

Each Story Map card of the release is an activity with its stories in this release. Show every card once, in board order:

- the activity;
- how it will be declared: a card with one story is a Story; a card with two or more is an Epic with one Story per story;
- its stories, by task, each with the original estimate in hours that `start` proposes for it (`start`'s `references/estimation.md`); an Epic has none.

Then ask the maintainer to confirm the release. They can change any estimate before confirming; keep their value as it is. Only an explicit confirmation counts: until they confirm, nothing is created in Jira, not even when they ask to skip the review.

If they ask for a change (a story in or out, moved to another release or activity, reworded), it is made on the Story Map, never only in what will be declared: Confluence is the only source. Make it with Gemba Product's `story-map` skill if it is installed, or ask the person to make it on the board. Then read the release again (step 3) and show it again from step 4. Until that new reading, show no release at all, neither as it would look after the change nor as it is before it: only a reading of the board after the change counts. Each change goes through the board and a new reading before declaring.

## Without a connection

If there is no connection to Confluence, say that the brief and the Story Map are read only from Confluence and could not be read. Do not ask for a copy in the repository. If the person pastes the board as Confluence returns it, read that the same way.

## Style

- Conversation in the project's `Language`; headings and labels in English.
- No emojis or filler.
