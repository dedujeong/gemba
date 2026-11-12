# Jira calls

Every call Gemba Code makes to Jira, so each skill asks only for the fields it uses and the session does not fill with avatars, type descriptions and whole issues. Use the call as written: the operation, its `inputs` and its `responseFields`. Never ask for the `view` presets of the direct tools; `responseFields` only works through `executeRead` and `executeWrite`, so every call goes through them.

`cloudId` is a top-level argument of every call, a sibling of `name` and `inputs`, never inside `inputs`.

## Read an issue

To take, review or close an issue: its state, its type, its criteria and its links.

- `executeRead` → `getJiraIssue`
- `inputs`: `{"issueIdOrKey": "<KEY>", "fields": ["summary", "status", "issuetype", "description", "components", "fixVersions", "parent", "issuelinks"], "fieldsByKeys": true}`
- `responseFields`: `["key", "fields.summary", "fields.status.name", "fields.issuetype.name", "fields.description", "fields.components.name", "fields.fixVersions.name", "fields.parent.key", "fields.issuelinks.type.name", "fields.issuelinks.inwardIssue.key", "fields.issuelinks.inwardIssue.fields.status.name", "fields.issuelinks.outwardIssue.key", "fields.issuelinks.outwardIssue.fields.status.name"]`

A link of type `Blocks` with an `inwardIssue` is an issue that blocks this one.

## Read the state of an issue

To check a handoff or save one: key, summary, state and fix version, nothing else.

- `executeRead` → `getJiraIssue`
- `inputs`: `{"issueIdOrKey": "<KEY>", "fields": ["summary", "status", "fixVersions"], "fieldsByKeys": true}`
- `responseFields`: `["key", "fields.summary", "fields.status.name", "fields.fixVersions.name"]`

## Search issues

To list the children of an Epic (`parent = <KEY> ORDER BY Rank`) or the open issues of a version (`project = <Jira Project> AND fixVersion = "<version>" AND statusCategory != Done ORDER BY Rank`).

- `executeRead` → `searchJiraIssuesUsingJql`
- `inputs`: `{"jql": "<JQL>", "fields": ["summary", "status", "issuetype", "issuelinks"], "maxResults": 50}`, and `nextPageToken` for the next page while `isLast` is false
- `responseFields`: `["issues.key", "issues.fields.summary", "issues.fields.status.name", "issues.fields.issuetype.name", "issues.fields.issuelinks.type.name", "issues.fields.issuelinks.inwardIssue.key", "issues.fields.issuelinks.inwardIssue.fields.status.name", "isLast", "nextPageToken"]`

## Read the changelog

To compute the time worked in a state with `state_time.py`.

- `executeRead` → `listJiraIssueChangelogs`
- `inputs`: `{"issueIdOrKey": "<KEY>", "maxResults": 50}`, and `startAt` for the next page while `total` is larger than what was read
- `responseFields`: `["total", "startAt", "values.created", "values.items.field", "values.items.fromString", "values.items.toString"]`

Save every page, in one list, to a temporary file for the script.

## Find a project

To check that the Jira Project the person names exists. The search also matches names, so only a result with exactly that key counts.

- `executeRead` → `listJiraProjects`
- `inputs`: `{"query": "<key>"}`
- `responseFields`: `["values.key", "values.name", "isLast"]`

## List the components

To choose the component of a new issue.

- `executeRead` → `listJiraProjectComponents`
- `inputs`: `{"projectIdOrKey": "<Jira Project>"}`
- `responseFields`: `["values.name", "values.description", "total", "isLast"]`

## List the versions

To find the earliest unreleased fix version, or the dates of one.

- `executeRead` → `getJiraProjectVersions`
- `inputs`: `{"projectIdOrKey": "<Jira Project>"}`
- `responseFields`: `["values.name", "values.released", "values.startDate", "values.releaseDate"]`

## Log the time

To log the real time worked in a state, with the `started` and `timeSpent` that `state_time.py` prints.

- `executeWrite` → `addOrEditJiraIssueWorklog`
- `inputs`: `{"issueIdOrKey": "<KEY>", "timeSpent": "<timeSpent>", "started": "<started>"}`
- `responseFields`: `["id", "timeSpent", "started"]`

## Create an issue

- `executeWrite` → `createJiraIssue`
- `inputs`: `{"projectKey": "<Jira Project>", "issueType": "<work type>", "summary": "<Summary>", "contentFormat": "html", "description": "<HTML>", "priority": "<priority>", "additional_fields": {...}}`, and `parent` for the Story of an Epic. `additional_fields` holds `fixVersions` (`[{"name": "<version>"}]`), `components` (`[{"name": "<component>"}]`, never for an Epic), `timetracking` (`{"originalEstimate": "<n>h"}`, never for an Epic) and `duedate` (an Epic only).
- `responseFields`: `["key"]`

## Link two issues

- `executeWrite` → `createJiraIssueLink`
- `inputs`: `{"linkType": "Blocks", "inwardIssue": "<blocker KEY>", "outwardIssue": "<blocked KEY>"}`
- `responseFields`: `["message"]`

## Edit an issue

Only while the issue is in Backlog.

- `executeWrite` → `editJiraIssue`
- `inputs`: `{"issueIdOrKey": "<KEY>", "contentFormat": "html", "fields": {"description": "<HTML>", ...}}`
- `responseFields`: `["key"]`
