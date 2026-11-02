# Plan limits

A decision that depends on the plan of a provider (hosting, database, maps, email, monitoring) is proposed with limits that were looked up, never recalled. The model's memory of plans is old: providers change prices, limits and terms often.

## What to verify

For each provider the decision relies on, free plan or paid:

- Price, and whether a card is required to start.
- Usage limits that the MVP can reach: builds, requests, storage, bandwidth, CPU time, rows.
- Commercial use: whether the plan allows charging customers.
- Pause or expiry: whether the project is paused or deleted after a period of inactivity.

Verify only what the decision depends on. Do not collect every limit of a plan. A price or limit stated about an alternative is a limit too: cite it, or describe the alternative without it. "It is free", "it allows commercial use" and "it is paid" are statements about a plan like any number.

## How to verify

Search the web and read the provider's own pricing or terms page. A blog post or a forum answer is a lead, not a source: find the provider's page behind it.

## How to cite

Write the source next to each limit, in the same form every time, so the person can check it:

`<limit> (<page title>, <URL>, consulted <YYYY-MM-DD>)`

Example: `uso comercial no permitido en el plan Hobby (Vercel Fair Use Guidelines, <URL>, consulted 2026-11-02)`.

The date matters: it tells the reader how old the limit is.

## When the search does not settle it

If you cannot search because there is no web tool in the session, say so once and go on: propose every decision with its option and alternatives as usual, and label every plan limit Assumption. The missing search never turns a decision into "candidates, not chosen yet".

If the search finds nothing, or two sources disagree, say so and label the limit Assumption, as `../../pitch/SKILL.md` section 4 defines. Do not state it as a fact and do not drop it: a limit the decision depends on is either cited or marked.

## What memory gets wrong

Two cases from a real run, where a decision made from memory would have been wrong:

- Vercel Hobby does not allow commercial use. A product that charges its customers needs another host (that run chose Cloudflare Pages).
- The public OpenStreetMap tile server is not meant for production use. A map in production needs a tile provider, and the decision waits on a Spike to choose one.
