---
type: llm
---
There is no access to the repository or the remote, so saying that nothing was run and writing the commands that would be run is expected: a command counts as done when it is written in the response, in order.

The GitHub release goes on the tag of the version, with the repository's notes template.

PASS if the response creates a GitHub release (`gh release create`) on the tag `taller--v0.2.0`, titled exactly `Taller v0.2.0` (product name and version, not the tag), and drafts its notes following `.github/release-notes.md`: an opening sentence for the person who uses the plugin, only the sections that have content (Added for the new service registration, Fixed for the late reminder), and a **Full Changelog** line that compares `taller--v0.1.0` with `taller--v0.2.0`. Sections with nothing, such as Changed and Removed, are left out.
FAIL if the title is the tag name or lacks the product name, if the release is not created on that tag, if the notes ignore the template, keep empty sections or placeholders, describe how it was built instead of what the person can do, or if the Full Changelog compares against anything other than the previous release of the same plugin.
