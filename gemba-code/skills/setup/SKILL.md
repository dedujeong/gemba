---
name: setup
description: Prepare a project for Gemba Code by writing its Gemba block in the project's CLAUDE.md: the Jira project, the Confluence space, the integration mode and the language. Use when someone sets up a repository for the method, says "configura el proyecto" or "setup", when a project value changes (a new collaborator, another space), or when another skill finds no Gemba block in CLAUDE.md.
---

# Set up the project

You write the project's data in its `CLAUDE.md`, so every session knows where to declare and publish without asking. The data is the Gemba block in `assets/gemba-block.md`. You write nothing else to the repository.

## 1. Read what is there

Read `CLAUDE.md` at the root of the repository, if it exists. A `## Gemba` section already in it is the starting point: its values stay unless the person changes them.

## 2. Gather the values

Each value comes from what the person said, from the existing block, or from a read in Jira or Confluence. Get the cloudId once with `getAccessibleAtlassianResources`.

| Field | Where it comes from |
|---|---|
| Jira Project | The key the person names. Check that it exists with `executeRead` → `listJiraProjects` (`query`: the key); the search also matches names, so only a result with exactly that key counts. If they named none, list the visible projects and ask which one. |
| Confluence Space | The key the person names. Check that it exists with `executeRead` → `listConfluenceSpaces` (`keys`: the key). If they named none, list the spaces and ask which one. Each product has its own Jira project and its own Confluence space. |
| Integration | Only the person knows it: `merge` or `pull request`, as the asset explains. |
| Language | The language the Product Brief in that space is written in, read with `searchConfluence` and `getConfluenceContent`. If there is no brief, ask. |

A value you cannot read and the person did not give is asked, never assumed: no default, no guess from another value (the space is not the Jira key just because they often match, and working alone is not assumed). Ask for every missing value in one message, and write nothing until they are answered. A key that does not exist in Jira or Confluence is also asked again.

Without a connection to Jira or Confluence, use what the person gave and say that it could not be checked.

## 3. Write the block

Follow `assets/gemba-block.md`: same heading, same fields, same order.

- No `CLAUDE.md`: create it with only the block.
- A `CLAUDE.md` without a `## Gemba` section: add the block at the end. Keep everything that was there, unchanged.
- A `CLAUDE.md` with a `## Gemba` section: update its four fields in place. Keep its other lines and the rest of the file, unchanged. The file ends with one `## Gemba` section and each field once.

If you cannot write files, put the whole resulting `CLAUDE.md` in the reply and say that nothing was written.

## 4. Report

Show the block as it was written, and say which values were read from Jira or Confluence and which the person gave. Nothing else.

## Style

- Conversation in the project's language; headings, field names and labels in English.
- No emojis or filler.
