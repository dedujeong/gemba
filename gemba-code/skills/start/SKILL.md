---
name: start
description: Declare one Jira issue with the template of its work type and its priority, component, fix version and blocking links, and handle every change to an existing issue, which is only edited in Backlog. Use when someone says "declara", "hay un bug", "nueva tarea", "registra un spike" or describes work to track; when someone asks to change, edit or add a criterion to an issue ("cambia la descripción de", "agrégale un criterio a"); and when version-start declares a release card.
---

# Start an issue

You declare one unit of work in Jira so it can be built: the right work type, a description from its template, and every field filled. Declaring is the whole job; you do not implement anything. A card that version-start hands over is declared exactly the same way.

## 1. Find the project

Read the `## Gemba` section of the project's `CLAUDE.md`: `Jira Project`, `Confluence Space` and `Language`. If it is missing, propose running `setup` first and stop. Get the cloudId once with `getAccessibleAtlassianResources`.

Read the Product Brief in the Confluence space for its actors and business rules. The issue content is written in `Language`.

## 2. Choose the work type

Declare one issue per request.

| Work type | Use it when |
| --- | --- |
| Epic | A Story Map card with two or more stories: a goal done through its children, never by itself, inside one version |
| Story | Something a user can do that they could not before |
| Task | Technical work no user sees but other issues need: repo, stack, deploy, roles |
| Bug | Something already delivered does not do what it should, and the issue that delivered it is Done. If that issue is not Done yet, it is not a bug: say so and propose adding the case to that issue's criteria while it is in Backlog |
| Spike | A question a decision depends on, answered in a fixed timebox |

## 3. Fill the fields

| Field | Rule |
| --- | --- |
| Summary | English, understandable on its own, no parentheses. The branch comes from the key and the summary |
| Priority | Highest, High, Medium or Low, by how much other work waits on it |
| Component | The part of the repository the change touches, in lowercase; it is also the commit scope. Read the existing ones with `executeRead` → `listJiraProjectComponents` and reuse one when it fits; naming a new one in the create call creates it. An Epic has no component |
| Fix version | The one named by the person or by version-start. Otherwise the earliest unreleased version (`executeRead` → `getJiraProjectVersions`). If there is none, stop and say that version-start has to create it. Never create a version here |
| Due date | Epic only, set by the maintainer. Ask for it if they did not give it |
| Blocks / is blocked by | Ask what must exist first. Search the version's open issues (`fixVersion = "<version>" AND statusCategory != Done`) and propose the blockers you find |

Ask for anything above you cannot read or infer from what the person said, in one message.

## 4. Write the description

Use the template of the work type in `assets/`: `epic.md`, `story.md`, `task.md`, `bug.md` or `spike.md`. Write it in HTML from the first version, so block cards and other rich content are right: `<p>`, `<h3>`, `<ul><li>`, `<ol><li>`, `<code>`.

- Content in `Language`; section headings in English, as H3. The opening paragraph has no heading.
- Every list is bulleted, with no checkboxes. Only Steps to reproduce is numbered.
- Code (field names, routes, commands, error messages) goes in code style.
- No bold. Never mention Gemba Code or where the issue came from.
- Only the sections of the template; omit a section when there is nothing to put in it.
- Business rules and out-of-scope items come only from the Product Brief and the Story Map, in their words. When something needed is missing, ask.
- The issue is the request, not the specification: generic referents, no invented sample data, and only what the person observes, never how it is achieved.

## 5. Show it, then create it

Show the declaration in one compact block: work type, summary, priority, component, fix version, due date, blockers and the description. Wait for the person's OK. When version-start hands over a card, the maintainer already confirmed the whole version: create it without asking again.

Then:

1. Create the issue with `createJiraIssue`: `contentFormat: "html"`, the description, `priority`, and in `additional_fields` `fixVersions` (`[{"name": "<version>"}]`), `components` (`[{"name": "<component>"}]`, never for an Epic) and `duedate` for an Epic. New issues land in Backlog.
2. Create each blocking link with `executeWrite` → `createJiraIssueLink`: `linkType: "Blocks"`, `inwardIssue` the blocker, `outwardIssue` the blocked issue.

Declaring a Spike creates only the issue; its findings page is created when the Spike starts.

Without a connection to Jira, write in the reply the exact create call and links you would send, and say that nothing was created.

## 6. Edit only in Backlog

When someone asks to change an issue, read its status first. In Backlog, edit it with `editJiraIssue` (`contentFormat: "html"`), following the same template. In Implement, Review or Done, do not edit it: say that an issue is edited only while it is in Backlog, and propose a new issue for the change instead.

## 7. Report

Reply with the keys as links, one line each, and anything you decided for the person (a work type, a priority, a blocker). Nothing else.
