# Gemba Code

Development for Claude Code: from a closed Story Map to released versions, with every issue declared in Jira and driven to done.

Gemba Product ends discovery with a closed Story Map. Gemba Code picks it up there: it opens a version from the release you closed, declares its issues in Jira with their acceptance criteria and estimates, and takes each one from its branch to the merge until the version is released.

## Install

```bash
/plugin marketplace add dedujeong/gemba
/plugin install gemba-code@gemba
```

## Requirements

- Claude Code.
- The Atlassian connector, with access to the product's Jira project and Confluence space.
- A closed Story Map from Gemba Product in that Confluence space.
