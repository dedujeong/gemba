# Gemba method

These rules apply to every session in a project that uses Gemba Code. The project's data (Jira project, Confluence space, integration and language) is in the `## Gemba` section of its `CLAUDE.md`; if that section is missing, propose running `setup` before anything else. Each rule says, after "Prevents", the failure it exists for.

## Work items

- Work starts only from a Jira work item in the current fix version. If there is none, propose declaring it before touching code. Prevents: changes with no trace back to what was agreed.
- An item blocked by another open item is not started. Jira does not enforce it, so check the item's links when taking it. Prevents: building on work that does not exist yet.
- The acceptance criteria (Story) or Done when (Task, Bug, Spike) are the contract. If they turn out wrong or incomplete, say so and update the item before the code changes, not after. Prevents: reviewing against a contract nobody agreed.
- An item is edited only while it is in Backlog. Prevents: a contract that changes while it is being built or reviewed.
- Work types: an Epic groups the work of one Story Map card inside one version and has no branch; a Story is something a user can do that they could not before; a Task is technical work no user sees; a Bug is something already Done that does not do what it should (if its item is not Done, add the case to that item's criteria instead); a Spike answers a question in a fixed timebox. Prevents: work filed where nobody will look for it.

## Spike findings

- A Spike's answer lives in a findings page in the product's Confluence space, under `Work` > `Spikes`, never in the issue or the repo. The page is created when the Spike starts, titled `<KEY> <Summary>` exactly as in Jira, with the issue as a block card at the top and then Recommendation, Options, Impact on scope and Sources. Its status is Rough draft when created and Verified when the Spike closes. The issue links to it once. Prevents: answers lost in a conversation or left as artifacts in the repo.

## Work cycle

- Backlog: the item is declared and waits.
- Implement: when its branch is created from `develop`, before the first change.
- Review: when its implementation is finished, with every test green, before the merge. No item reaches Done without Review.
- Done: when its branch is merged into `develop` and pushed. A Spike reaches Done when its findings are published and its branch is deleted.
- Cancelled: from any state, when the person drops the item. Its branch, if any, is deleted without merging.
- When the item leaves Implement and when it leaves Review, log the real time worked in that state on the item, never a copy of the estimate.

Prevents: a board that does not say where each item really is, and estimates that can never be compared with what happened.

## Branches

- `main` is production and `develop` is integration. Nothing is committed on them directly. Prevents: unreviewed changes in production.
- One branch per Story, Task, Bug or Spike, created from `develop` and named `<type>/<KEY>-<slug>`: the type in lowercase (`story`, `task`, `bug`, `spike`), the Jira key and the Summary as a slug of lowercase letters, digits and single hyphens (`story/ABC-12-export-invoices-as-csv`). An Epic has no branch. A Spike's branch is never merged. Prevents: changes that cannot be traced to their item.
- Only the branch carries the key; commits do not repeat it.

## Merges

How a branch reaches `develop` depends on `Integration` in the Gemba section:

- `merge`: merge the branch locally into `develop` with `git merge --no-ff` and Git's default message (`Merge branch '<branch>' into develop`), push `develop` and delete the branch. Work branches are not pushed.
- `pull request`: push the branch and open a pull request into `develop`. The maintainer reviews it and decides the merge, always as a merge commit.

In both: never squash, and never rebase a branch onto `develop` or `main`; to bring in new work from `develop`, merge it into the branch. Prevents: lost history and rewritten commits that someone else already has.

## Commits

- One line, with no body or footer: `<type>(<scope>): <description>`. Types: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, `test`. The scope is optional and is one of the project's Jira components, in lowercase. A breaking change adds `!` before the colon and its description says what breaks. The only exceptions are the merge commit and a repository's `Initial commit`. Prevents: a history nobody can read or filter.
- The description starts with a verb in the imperative mood, has no final period and keeps proper names in their canonical form (Jira, GitHub, API).
- A commit is one coherent change you would revert as a whole, and it leaves the branch working. Its tests and docs go in the same commit. Prevents: reverts that break something else.
- A correction to a commit not yet pushed is folded into it (`git commit --fixup`, then `git rebase --autosquash`). This is the only rebase allowed.

## Test-driven development

- Every acceptance criterion becomes a test before the code that satisfies it: red (it fails for the expected reason), green (the least code that passes), refactor (with the tests still green). A Bug starts with a test that reproduces it and fails. Prevents: criteria that nothing checks.
- Red is never committed: the test and the code that makes it pass go in the same commit.
- A test is never skipped, weakened or deleted to get green. If the test is wrong, say why and fix it in its own commit. Prevents: a green suite that hides a failure.
- Before the merge into `develop`, every test passes.

## Versions and releases

- Each Story Map release is a Jira fix version named `<Product> vX.Y.Z`. Each release raises the minor number (`v0.1.0`, `v0.2.0`); a bug fix on a released version raises the third (`v0.1.1`). The major number stays at 0 until the first paying customer. The version in the code is bumped only at the release, never per commit. Prevents: version numbers that say nothing about what shipped.
- The release is a Task in the fix version, `Release <Product> vX.Y.Z`, blocked by every other item of the version and the last to close. Its branch carries a single commit that bumps the version.
- Once that Task is merged into `develop`: merge `develop` into `main` with `--no-ff`, push `main` and tag the merge `vX.Y.Z` (in a repository with several Claude plugins, `claude plugin tag <plugin> --push`, which tags `<plugin>--vX.Y.Z`). Create the GitHub release on that tag, titled `<Product> vX.Y.Z`. Then release the fix version in Jira and move the Task to Done.
- A version does not close while any item of its fix version is outside Done or Cancelled. Prevents: releasing a version with work still open, or skipping a step of the close.

## Language

- Talk with the person in the project's `Language`. Headings, labels and field names stay in English.
