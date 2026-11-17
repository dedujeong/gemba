# Layout principles

The code layout comes from the work of the release, not from a fixed template. Two principles decide it. Apply them to the activities and stories of the current release and to its data model; the conventions of the framework are not decided again.

## 1. What changes together stays together

Code that a story changes in one step lives in one place. Group by the domain the product talks about (a booking, a schedule), not by the kind of file (controllers, services, models): a story that touches every layer then touches every folder.

- A domain gets its own folder when its stories change it together and it has its own data.
- Something that does not change with a domain, or serves several of them, is not forced into one.

## 2. Dependencies go in one direction, through a public entry

A domain depends on another only through its public entry, one file that says what the domain offers. Nothing reaches inside another domain, and dependencies never go back: if A uses B, B does not use A.

- Each domain has one entry file; the rest of its files are private.
- The direction is written down: which domain may use which.
