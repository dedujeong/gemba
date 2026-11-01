---
type: llm
---
There is no access to the repository or the remote, so saying that nothing was run and writing the commands that would be run is expected: a command counts as done when it is written in the response, in order.

The repository holds several Claude plugins, and the plugin of the product is `taller`.

PASS if, once `main` is pushed, the tag is created with `claude plugin tag taller --push` (which tags `taller--v0.2.0`), or with a tag named exactly `taller--v0.2.0` pushed to the remote.
FAIL if the tag is named only `v0.2.0` or after anything other than the plugin and version, if it is created before `main` is pushed, or if no tag is created and pushed.
