---
type: llm
---
The release Task is merged into `develop`, and the maintainer asks to publish.

PASS if the commands bring all of `develop` into `main` with a merge commit (`git merge --no-ff` of `develop` while on `main`, with Git's default message) and push `main` to the remote. Checking out `main` first is expected.
FAIL if `develop` is squashed or rebased into `main`, if `main` is not pushed, if anything is committed directly on `main` or `develop`, or if the response does not include this merge.
