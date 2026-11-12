---
type: regex
pattern: '(?=[\s\S]*"cloudId"\s*:\s*"(?:https://)?taller\.atlassian\.net)(?![\s\S]*getAccessibleAtlassianResources)'
target: last_message
---
Every call uses the Jira Site of the block as its cloudId, and the accessible resources are never requested.
