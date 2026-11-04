# ADR template

One live doc per decision, in the `Decisions` folder of the product's space. Headings stay in English; content in the person's language.

## Title

`ADR-000N <Decision>`: the number is four digits, one more than the highest `ADR-` already in the folder (`ADR-0001` when it is empty), and the decision is a short noun phrase (`ADR-0004 Cloudflare Pages`). The number is never reused or renumbered.

## Writing

The ADR is about the decision, not about who made it. A fact that comes from what a person said names their role (`the owner`, `the operator`, `the team`) and its source label (Interview, Secondhand or Assumption), never the person's name.

Every path, file, folder, column, domain and command the decision names is written as code (`db/migrations`, `starts_at`, `supabase db push`) each time it appears in the body. The title is plain text.

## Sections

Five H2 sections, always in this order.

### Context

The story of the current release or the constraint of the brief that makes the decision necessary, in one or two sentences.

### Decision

The option chosen, in one sentence, and why it wins here.

### Alternatives

Every alternative that was weighed, including those the person rejected in the review, each with what it offers and why it lost. A rejected alternative is recorded, not dropped.

### Consequences

What the decision commits the product to: cost, operation, what gets harder.

### Source

A block card (a link with `data-card-appearance="block"`, directly under the heading and with no empty paragraph between them) to the page or source the decision rests on: the Product Brief, the Story Map or the provider page cited for a plan limit (`references/plan-limits.md`).

```html
<h2>Context</h2>
<p>...</p>
<h2>Decision</h2>
<p>...</p>
<h2>Alternatives</h2>
<ul>
  <li>...</li>
</ul>
<h2>Consequences</h2>
<p>...</p>
<h2>Source</h2>
<a href="SOURCE_URL" data-card-appearance="block"></a>
```
