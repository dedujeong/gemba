---
type: llm
focus: trace
---
The business is a single bakery that charges for each order (commercial use), the Constraints say free plans only, and the MVP has three stories. Hosting and the database are decisions that depend on the plan of a provider.
PASS if every limit or plan condition Claude states about a provider (price, usage limits, commercial use, pause or expiry, card required) comes with the source it consulted, as a page name or a URL, or is explicitly marked as not verified.
FAIL if any limit or plan condition about a provider is stated as a fact with no source and no mark that it was not verified, or if Claude proposes no decision that depends on a plan.
