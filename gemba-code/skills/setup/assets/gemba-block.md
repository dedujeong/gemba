# Gemba block

The section `setup` writes in the project's `CLAUDE.md`. Field names and their order are fixed, so other skills can read them.

```
## Gemba

- Jira Project: <Jira project key>
- Jira Site: <Jira site host>
- Confluence Space: <Confluence space key>
- Integration: <merge | pull request>
- Language: <language tag>
```

| Field | Value |
|---|---|
| Jira Project | The key of the product's Jira project, in uppercase (`ABC`). |
| Jira Site | The host of the Atlassian site of that project (`acme.atlassian.net`). Every skill uses it as the `cloudId` of its calls, so none has to ask for the accessible resources. |
| Confluence Space | The key of the product's Confluence space. |
| Integration | `merge` when the maintainer works alone: the branch is merged locally into `develop` with `--no-ff` and pushed. `pull request` when there are collaborators: each one opens a pull request and the maintainer reviews it and decides the merge. |
| Language | The language of the product and the conversation, as a language tag (`es-MX`, `en-US`). |

Components are not part of the block: they are created in Jira when an issue names them, so whoever needs them reads them from Jira at that moment.
