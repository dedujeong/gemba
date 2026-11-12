---
name: setup
description: Prepare a project for Gemba Code by writing its Gemba block in the project's CLAUDE.md: the Jira project, the Confluence space, the integration mode and the language. Use when someone sets up a repository for the method, says "configura el proyecto" or "setup", when a project value changes (a new collaborator, another space), or when another skill finds no Gemba block in CLAUDE.md.
---

# Set up the project

You write the project's data in its `CLAUDE.md`, so every session knows where to declare and publish without asking. The data is the Gemba block in `assets/gemba-block.md`. Besides it, you only set what the sections below name.

## 1. Prepare the repository

The method works on `main` (production) and `develop` (integration), so they exist before anything else. Run `python3 scripts/init_repository.py <project folder>`:

- A folder with no repository, or a repository with no commit yet, gets `git init`, an empty `initial commit` on `main` and `develop` created from `main`. The repository stays on `main`, and the files already in the folder stay uncommitted.
- A repository with `main` and no `develop` gets `develop` from `main`.
- A repository with `main` and `develop` keeps its branches and its history as they are.
- A repository with commits but no `main` is not touched: never rename a branch. The script says `main` is missing; ask the person what to do and go on with the rest of setup.
- A clone whose `main` or `develop` exists only on `origin` gets the local branch from the remote one.
- When git has no name and email for the initial commit, the script says so: ask the person for them, set them in the repository with `git config user.name` and `git config user.email`, and run the script again.

If you cannot run commands, put the command in the reply and say that it was not run.

## 2. Read what is there

Read `CLAUDE.md` at the root of the repository, if it exists. A `## Gemba` section already in it is the starting point: its values stay unless the person changes them.

## 3. Gather the values

Each value comes from what the person said, from the existing block, or from a read in Jira or Confluence. Get the cloudId once with `getAccessibleAtlassianResources`.

| Field | Where it comes from |
|---|---|
| Jira Project | The key the person names. Check that it exists with `executeRead` → `listJiraProjects` (`query`: the key); the search also matches names, so only a result with exactly that key counts. If they named none, list the visible projects and ask which one. |
| Confluence Space | The key the person names. Check that it exists with `executeRead` → `listConfluenceSpaces` (`keys`: the key). If they named none, list the spaces and ask which one. Each product has its own Jira project and its own Confluence space. |
| Integration | Only the person knows it: `merge` or `pull request`, as the asset explains. |
| Language | The language the Product Brief in that space is written in, read with `searchConfluence` and `getConfluenceContent`. If there is no brief, ask. |

A value you cannot read and the person did not give is asked, never assumed: no default, no guess from another value (the space is not the Jira key just because they often match, and working alone is not assumed). Ask for every missing value in one message, and write nothing until they are answered. A key that does not exist in Jira or Confluence is also asked again.

Without a connection to Jira or Confluence, use what the person gave and say that it could not be checked.

## 4. Write the block

Follow `assets/gemba-block.md`: same heading, same fields, same order.

- No `CLAUDE.md`: create it with only the block.
- A `CLAUDE.md` without a `## Gemba` section: add the block at the end. Keep everything that was there, unchanged.
- A `CLAUDE.md` with a `## Gemba` section: update its four fields in place. Keep its other lines and the rest of the file, unchanged. The file ends with one `## Gemba` section and each field once.

If you cannot write files, put the whole resulting `CLAUDE.md` in the reply and say that nothing was written.

## 5. Turn off the Claude attribution

Claude Code adds its own attribution lines to commits and pull requests, and the method's commits are one line with no footer. In `.claude/settings.json` at the root of the repository, set `"attribution": {"commit": "", "pr": ""}`. If the file does not exist, create it with only that key. If it exists, add or replace only the `attribution` key. Keep every other key and the rest of the file unchanged. If the value is already there, change nothing. If you cannot write files, put the whole resulting file in the reply and say that nothing was written.

## 6. Ask for confirmation on every git push

Nothing may reach the remote without the maintainer seeing it. The plugin's `PreToolUse` hook already asks too in a project with this block: naming the branch and the remote for a `git push` it can read, and with a generic reason for any other command that contains one (a `bash -c` string, `sudo`, a shell keyword). The rule of this step is the floor under it: a permission rule is enforced by Claude Code itself, wins over any allow rule and does not depend on a script. In `.claude/settings.json`, set `"permissions": {"ask": ["Bash(git push *)"]}`. The file already exists after step 5. Add the `permissions` key if it is missing; if it exists, add the rule to its `ask` list and do not add it twice. Keep every other key and every other rule unchanged. If the rule is already there, change nothing.

When the `Integration` of the block is `pull request`, the maintainer merges, never Claude: `permissions.deny` gets `Bash(gh pr merge *)` in the same file, the same way (add the `deny` list if it is missing, do not add it twice, keep every other key and every other rule). The plugin's hook denies `gh pr merge` too; this rule is the floor under it. In `merge` mode write no deny rule, and leave one that is already there as it is.

If you cannot write files, put the whole resulting file in the reply and say that nothing was written.

## 7. Write the base .gitignore

Claude's local files and the Spikes' worktrees must never reach the repository. Run `python3 scripts/write_gitignore.py <repository root>/.gitignore`. It creates the file when it does not exist, and otherwise adds only the entries it lacks, so the lines already there are neither deleted nor reordered. The base is three groups, each with a comment in English:

- `.claude/settings.local.json` and `CLAUDE.local.md`, the personal Claude Code files;
- `.claude/worktrees/`, the worktrees of the Spikes;
- `.gemba/sessions/`, the session handoffs.

Never edit the `.gitignore` by hand. If you cannot run commands, put the command in the reply and say that it was not run.

## 8. Write the license

Only when the repository has no `LICENSE` (nor `LICENSE.md` or `LICENSE.txt`). When it has one, ask nothing and leave it as it is; the README reads its name in step 9.

1. Ask which license to use: Apache-2.0, MIT or none. Offer exactly those three and do not choose for the person. In the same message, for Apache-2.0 or MIT, propose the data and ask the person to confirm or correct it: the holder (`git config user.name`), the holder URL (the owner of `git remote get-url origin` as `https://github.com/<owner>`; none when there is no remote) and the year (the current one). Never write the files before the person confirms.
2. Run `python3 scripts/write_license.py <repository root> <Apache-2.0|MIT|none> --holder "<holder>" --year <year> --product "<product name>"`, adding `--holder-url <url>` when there is one. The product name is the title of the Product Brief. The script fetches the official text when it runs, writes the `LICENSE` (inside it, for MIT, the holder and the year) and, for Apache-2.0, the `NOTICE`; with none it writes nothing. You never type or paraphrase a license text yourself, and you never keep a copy of one.
3. If the script cannot read the official text it writes nothing: say what is missing, which license text and which address, and go on with the rest of setup.

The license is not saved in the Gemba block. If you cannot run commands, put the command in the reply and say that it was not run.

## 9. Write the project README

Every project starts from the same README. Only when the repository has no `README.md` at its root, write it from `assets/readme.md`:

- The product name, the one-line description and What it is come from the Product Brief you read in step 3: the name from its title, the description from its Primary job, What it is from its Problem and its actors. If there is no brief, those fields stay as fields to fill and you say so.
- Install, Run and Test come only from what the repository states: the commands in the project's `CLAUDE.md` and in its package or build files. Install, Run and Test are written only when the repository states their commands: a section with no command is left out whole, heading included. Inside Install, Requirements lists only the requirements the repository states, and the line is removed when it states none; inside Run, the Environment variables line follows the same rule. Never invent a command, a version or a variable.
- A project with no stack yet, whose repository states no command, gets only the title, its one-line description and What it is, plus the License section when a license is known.
- The content is in the project's `Language`. The section names and every field that stays to fill are kept exactly as the template has them, in English, so they can be found. A requirement is the name of the tool or dependency in its canonical form with its version (`Node.js 22`, `Supabase CLI`), never a sentence or the hint of the field.
- The License section is kept only when a license is known: the one chosen in step 8, or the one read from the title of the existing `LICENSE` ("Apache License" is Apache-2.0, "MIT License" is MIT). Its year, holder and holder URL are the ones confirmed in step 8; what is not known stays as a field to fill. Write the sentence about the NOTICE only for Apache-2.0, and the section without the sentence about the NOTICE for MIT. With none, or a title you do not recognize, remove the whole License section and say so.
- Remove the comment at the top of the template.

If you cannot write files, put the whole README in the reply and say that nothing was written.

When the repository already has a `README.md`, never replace or rewrite it, and leave every line of it as it is. Compare its headings with the sections of the template (What it is, Install, Run, Test and, when a license is known, License): a heading that covers the same content counts as present, for example "Installation" for Install or "Usage" for Run. Propose only the sections it lacks, written from the template with the data above, and do not write them: the person decides whether to add them. The rule that leaves out a section with no command applies only to a README that setup writes: A proposed Install, Run or Test whose command the repository does not state is still proposed, with its command as a field to fill, never an invented one. If it has all four, say so and propose nothing.

## 10. Write the code layout

`architecture` decides where each file goes and records it as an ADR, so every session can know it without asking. Search the `Decisions` folder of the Confluence Space for the ADR of the code layout, and read it with `getConfluenceContent`. Use only an ADR whose page status is Verified (accepted) and that no later ADR replaces. A Rough draft or a replaced ADR is not used.

- With that ADR, write a `## Code layout` section in `CLAUDE.md`, right after `## Gemba`, with exactly four lines, each with a bold label in English, copied from the Decision of the ADR and written in the project's `Language`:
  - **Folders:** the folders by domain and the routes.
  - **Tests:** where the tests go.
  - **File names:** how the files are named.
  - **Migrations:** where the migrations go; `not applicable` when the ADR says it does not apply.
- Every path, folder and file the line names is written as code. Anything else the ADR says stays in the ADR: the section has no other line, and no source line.
- A `CLAUDE.md` that already has a `## Code layout` section: it is updated in place, keeping the rest of the file unchanged. If it already says the same, change nothing.
- Without that ADR, write nothing: invent no layout, not even a common one for the stack. Say that `architecture` has not decided it yet.

Without a connection to Confluence, write nothing and say that the ADR could not be read. If you cannot write files, put the section in the reply and say that nothing was written.

## 11. Report

Say first what was done with the repository (created with `main` and `develop`, `develop` created, nothing changed, or `main` missing and asked). Show the block as it was written, and say which values were read from Jira or Confluence and which the person gave. Add, for the attribution, for the git push confirmation, for the gh pr merge deny (only in pull request mode), for the `.gitignore`, for the license, for the README and for the code layout, whether it was set, already there or not written, for a README written the sections left out because the repository states no command for them, for an existing README the sections that were proposed, and for the code layout, when it was not written, that `architecture` has not decided it yet. Nothing else.

## Style

- Conversation in the project's language; headings, field names and labels in English.
- No emojis or filler.
