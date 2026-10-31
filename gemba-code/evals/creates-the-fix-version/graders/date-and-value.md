---
type: llm
---
The maintainer gave the delivery date 2026-11-20. The current release on the board is labeled "Release 2" with the description "The shop owner records each vehicle and reminds customers the day before.". A fix version's description says only the value it delivers.

The version also has a start date (2026-11-02, in `startDate`); it is a different field, expected, and judged elsewhere. Judge only the release date and the description of the fix version Claude creates or drafts (the `releaseDate` and `description` of the create call). The rest of the response, such as the table of cards with their estimates, is not part of the version and does not count.

PASS if that release date is 2026-11-20 and that description states only the value the version delivers (for example the release's label description, or one sentence of value), with no list of stories, issues, dates or version numbers in it.
FAIL if the release date is missing or different, the description is missing, the description itself lists stories, issues, estimates, dates or version numbers, or no fix version is drafted.
