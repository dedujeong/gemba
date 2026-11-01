---
name: version-close
description: Close a version: check that no issue of its fix version is outside Done or Cancelled, and when one is, do not close and name the open ones; otherwise publish the release (merge develop into main, tag it, create the GitHub release) release the fix version in Jira and paint the delivered release gray on the Story Map. Use when someone says "cierra la versión", "publica la versión", "termina el release", "libera la versión" or that the work of a version is finished.
---

# Close a version

You close a version only when all its work is closed. Jira is the source: the issues of the fix version are read every time, never remembered from earlier in the conversation.

## 1. Find the project

Read the `## Gemba` section of the project's `CLAUDE.md`: `Jira Project` and `Language`. If it is missing, propose running `setup` first and stop. Get the cloudId once with `getAccessibleAtlassianResources`.

## 2. Check the issues

The version is the one the maintainer names. If they did not name one, take the earliest unreleased version (`executeRead` → `getJiraProjectVersions`).

Search its open issues with `searchJiraIssuesUsingJql`: `project = <Jira Project> AND fixVersion = "<version>" AND status NOT IN (Done, Cancelled)`. Leave out the release Task of the version, `Release <Product> vX.Y.Z`: it is the last to close, together with the close itself, so it never counts as open work.

- **Some issue is left:** do not close the version. List each one on its own line, as a link with its summary and status, and say that the version stays open until they are Done or Cancelled. Change nothing in them and stop there.
- **None is left:** say that no issue keeps the version open and go on with the close.

Without a connection to Jira, write the search you would make and take as its result the list the person gives you. Say that nothing was changed.

## 3. Publish the release

Only when the maintainer asks to publish and the release Task `Release <Product> vX.Y.Z` is already merged into `develop` with its bump commit. If it is not, say so and stop: the bump is the Task's work, not yours. The plugin is the one whose `plugin.json` that commit bumped, and the version is the one in the fix version name. This is the `merge` integration; the collaborative mode, where a pull request is reviewed, is not covered here.

Do these in order, and stop at the first one that fails:

1. `git checkout main`, `git merge --no-ff develop` with Git's default message, and `git push origin main`. Nothing is committed on `main` or `develop`; never squash or rebase.
2. `claude plugin tag <plugin> --push`. It checks that `plugin.json` and the marketplace entry agree and tags `<plugin>--vX.Y.Z`. Only after `main` is pushed.
3. `gh release create <plugin>--vX.Y.Z --title "<Product> vX.Y.Z" --notes-file <file>` on that tag. The title is the product name and version, never the tag. Write the notes in a temporary file outside the repository, following `.github/release-notes.md`: for the person who uses the plugin, what they can do and never how it was built, only the sections that have content, and a **Full Changelog** link comparing the previous release of the same plugin (`<plugin>--vA.B.C...<plugin>--vX.Y.Z`) with this one, never the latest tag of the repository. On the plugin's first release, link its commits up to the tag. Draw the notes from the version's issues, read from Jira.

Without access to the repository or the remote, write the commands and notes you would use and say that nothing was run.

## 4. Release the version in Jira

Only once the GitHub release exists. In this order:

1. Release the fix version: `executeDestructive` → `manageJiraProjectVersion` (`action: "update"`, `projectIdOrKey`, `versionId`, `released: true`, `releaseDate` the day of the release). Never create another version.
2. Move the release Task `Release <Product> vX.Y.Z` to Done (`transitionJiraIssue`, `to Done`), after logging its worklog if the work cycle asks for it. Move no other issue.
3. Read Jira again: `getJiraProjectVersions` for the fix version and a fresh `searchJiraIssuesUsingJql` for the Task. Report from that reading only, never from the responses of the update or the transition: the version released with its date, the Task in Done, plus the links of the tag and the GitHub release.

Without a connection to Jira, write the calls and the readings you would make, say where each reported fact would come from, and say that nothing was changed.

## Style

- Conversation in the project's `Language`; headings and labels in English.
- No emojis or filler.

## 5. Paint the delivered release gray

Only once the fix version is released. The Story Map is the board of the product's `Confluence Space`, found with `searchConfluence` (`space = "<Confluence Space>" AND type = whiteboard AND title ~ "Story Map"`). The release to paint is the row of the version: the first one not gray, the same one `version-start` opened.

1. Read the board with `getConfluenceContent` (`content_format: svg`) and keep the SVG whole, with its line numbers.
2. If Gemba Product's `story-map` skill is installed, recolor with it (its Recolor section, `--released` naming every delivered release, the ones already gray included). Otherwise take the ids of every sticky in the version's row, all of them and no other, and write them with `updateConfluenceContent`: one `update_elements_svg` with `ids="<ids>"` and `<attr fill="#f0f1f2"/>`, and the SVG of step 1 as `context.content`. Change only the fill: no text or position moves.
3. Read the board again. The response of the write is stale and says `ok` even when it changed nothing, so it is never the source: report the color of the release and the count of its stickies from this reading only. If a sticky of the release is not gray, say so and do not report it as done.

Without a connection to Confluence, write the calls and the second reading, say that the reported color would come from it, and say that nothing was changed.
