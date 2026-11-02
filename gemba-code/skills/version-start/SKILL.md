---
name: version-start
description: Open a version from the closed Story Map: read the Product Brief and the current release of the Story Map from Confluence, point out its open questions, have the maintainer confirm each card as a Story or an Epic, create the fix version named after the product and its number (Product vX.Y.Z) with its dates before anything is declared, and once declared put the key of each Story on its sticky of the Story Map. Use when someone says "abre la versión", "arranca la versión", "inicia el release", or that discovery closed a release and development starts.
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

Before showing anything, ask the maintainer once, in a single message, for what their request did not give: the start date and the delivery date of the version, and the hours of work per day. Wait for the answer. The hours per day are asked for every version and are never written to the `CLAUDE.md` or anywhere else; the dates are the ones step 6 uses. If the request already confirms the release and gives the Epics' due dates, do not ask: go on to steps 6 and 7.

Each Story Map card of the release is an activity with its stories in this release. Show every card once, in board order:

- the activity;
- how it will be declared: a card with one story is a Story; a card with two or more is an Epic with one Story per story;
- its stories, by task, each with the original estimate in hours that `start` proposes for it (`start`'s `references/estimation.md`); an Epic has none;
- one table with a row for every issue, the Epic's row too, and always the columns Priority, Component, Estimate and Blockers, as `start` would ask for them, proposed by you. Propose the components for the whole release together: the same part of the product carries the same component in every row, so one part never shows under two names (`api` and `backend`). Unify them before asking for the confirmation. Fill every cell: write `none` where a field is empty (an Epic has no component or estimate), and never leave a column out of a row, the Blockers of an Epic included. For an Epic, add its due date, which you propose and the maintainer can change.

Propose the Epics' due dates in board order, each one different from the others and none after the delivery date. Space them by the hours: an Epic's date is the day on which the hours of work since the start date, counted at the hours per day, reach the estimates of the Epics so far, rounded up to a whole day. An Epic fits when the sum of its Stories' estimates is not more than the hours available from the day after the previous Epic's due date (from the start date, for the first) through its own due date. When an Epic does not fit, say so before asking for the confirmation: name the Epic, its hours and the hours available. Never cut stories, lower estimates or move the dates on your own: the maintainer decides.

Propose the version number with the project's published versions: read them with `executeRead` → `getJiraProjectVersions`, save the result to a temporary file outside the repository (`mktemp`), run `python3 scripts/next_version.py "<Product>" <file>` and delete the file. It prints the name of the next release, which raises the minor number. If the maintainer says the version is a bug fix on a published one, run it again with `--fix`, which raises the third number. Show that name as the fix version, and use its number in the release Task. The maintainer confirms it or changes it together with the release.

After the cards, show the release Task `Release <Product> vX.Y.Z` that step 8 declares, with the number proposed above, its component, High priority and a 1h estimate. The component is one the project already has (`executeRead` → `listJiraProjectComponents`): the one where the version is bumped or, if none is, the component of the last card. In a project with no components yet, it is the component proposed for those same cards. A component the maintainer names for the Task is the one used. Never ask for it and never name one apart from these: it only labels the Task, and the maintainer can change it when they confirm.

Then ask the maintainer to confirm the release. They can change any estimate, priority, component, blocker or due date before confirming; keep their value as it is. Only an explicit confirmation counts: until they confirm, nothing is created in Jira, not even when they ask to skip the review.

If they ask for a change (a story in or out, moved to another release or activity, reworded), it is made on the Story Map, never only in what will be declared: Confluence is the only source. Make it with Gemba Product's `story-map` skill if it is installed, or ask the person to make it on the board. Then read the release again (step 3) and show it again from step 4. Until that new reading, show no release at all, neither as it would look after the change nor as it is before it: only a reading of the board after the change counts. Each change goes through the board and a new reading before declaring.

## 6. Create the fix version

Once the maintainer confirms the release, create its fix version before declaring anything, so every issue hangs from it.

- Name: `<Product> vX.Y.Z`, with the product name as the brief and the board give it and the number the maintainer confirmed in step 5, without asking for it again. If the maintainer changed it and it breaks the rule (each release raises the minor number, a bug fix on a released version raises the third, the major stays at 0 until the first paying customer), say so and ask again.
- Start date and release date: the ones the maintainer gave in step 5. Ask only for one that is still missing.
- Description: only the value the version delivers, from the release's row label on the board (the script returns it as the release description). No stories, issues, dates or numbers.

First list the project's versions with `executeRead` → `getJiraProjectVersions`. If one with the same name already exists, do not create another: say so and use it. Otherwise create it with `executeDestructive` → `manageJiraProjectVersion` (`action: "create"`, `projectIdOrKey`, `name`, `startDate`, `releaseDate`, `description`), then read the versions again and report the one that is there.

Without a connection to Jira, write the call you would make and say that nothing was created.

## 7. Declare the cards

Right after the fix version, declare every confirmed card through `start`, in that fix version, in board order: a card with one story as a Story with no Epic, a card with two or more as an Epic with one Story per story as its children. Hand `start` the card, its fields as the maintainer confirmed them and the Story Map link for an Epic's Source. The maintainer already confirmed the whole version in step 5: `start` creates each issue without asking again, and you do not ask either: do not offer a last chance to change something before creating. If the maintainer already confirmed the release in their request, do not show it again; go on to steps 6 and 7. Then report the keys, one line per card.

## 8. Declare the release Task

When all the cards are declared, declare the version's release through `start`, as a Task in the same fix version: summary `Release <Product> vX.Y.Z`, the component confirmed in step 5 (when the maintainer confirmed the release in their request, the one chosen by the rule of step 5: it is not a pending question and you do not offer to change it), with no blocking links. It is the last issue to close, because it waits for every other issue of the version to be Done or Cancelled, so publishing is part of the plan. Its Done when lists, in the project's `Language`:

- the version bump, integrated into `develop`;
- `develop` merged into `main`;
- the tag of the version;
- the release on GitHub, with its notes;
- the fix version released in Jira.

Like the cards, it is created without asking again. Report its key with the others.

## 9. Put the keys on the Story Map

When the cards and the release Task are declared, write the key of each Story on its sticky of the Story Map, so the board and Jira point to each other. Only the stickies of the stories get a key: never the Epic's, the activity's or a task's, nor an open question, and the release Task has no sticky. A Story is matched to its sticky by the story text read in step 3.

1. Read the board again with `getConfluenceContent` (`content_format: svg`) and save it whole, with its line numbers, to a temporary file outside the repository (`mktemp`). The patch is built on those line numbers, so it is sent right after this reading and never after an older one.
2. Write another temporary file with the keys, `{"<story text>": "<KEY>"}`, one entry per Story just declared: the Story of a card with one story and each child of an Epic.
3. Run `python3 scripts/write_keys.py <board file> <keys file>`. It prints one `replace_svg` per sticky, which keeps the story text and adds the key as a last line of the sticky. If it stops naming a text that is not in the current release, that story changed on the board after step 3: say so and write nothing.
4. Send the patch with `updateConfluenceContent`: `body.value` the patch as printed and `body.context.content` the SVG of step 1, whole.
5. Read the board again and run `python3 scripts/write_keys.py <new board file> <keys file> --check`. The response of the write is stale and says `ok` even when nothing changed, so it is never the source: report from the check which stickies carry their key. A story whose `ok` is false is reported as not written, never as done.

Delete the temporary files. Report one line per Story, with its key and whether its sticky carries it, and say what is missing if anything is.

## Without a connection

If there is no connection to Confluence, say that the brief and the Story Map are read only from Confluence and could not be read. Do not ask for a copy in the repository. If the person pastes the board as Confluence returns it, read that the same way, and for step 9 write the patch you would send and the reading and check you would make, and say that nothing was written on the board and that no key is reported as written.

## Style

- Conversation in the project's `Language`; headings and labels in English.
- No emojis or filler.
