# ADR template

One page per decision, in the `Decisions` folder of the product's space. Headings stay in English; content in the person's language.

## Title

`ADR-000N <Decision>`: the number is four digits, one more than the highest `ADR-` already in the folder (`ADR-0001` when it is empty), and the decision is a short noun phrase (`ADR-0004 Cloudflare Pages`). The number is never reused or renumbered.

## Sections

Five H3 sections, always in this order.

### Context

The story of the current release or the constraint of the brief that makes the decision necessary, in one or two sentences.

### Decision

The option chosen, in one sentence, and why it wins here.

### Alternatives

Every alternative that was weighed, including those the person rejected in the review, each with what it offers and why it lost. A rejected alternative is recorded, not dropped.

### Consequences

What the decision commits the product to: cost, operation, what gets harder.

### Source

A block card to the page or source the decision rests on: the Product Brief, the Story Map or the provider page cited for a plan limit (`references/plan-limits.md`).

```html
<h3>Context</h3>
<p>...</p>
<h3>Decision</h3>
<p>...</p>
<h3>Alternatives</h3>
<ul>
  <li>...</li>
</ul>
<h3>Consequences</h3>
<p>...</p>
<h3>Source</h3>
<p><a href="SOURCE_URL">Source page</a></p>
```
