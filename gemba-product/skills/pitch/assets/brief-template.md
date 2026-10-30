# Product Brief template

## Panels

Wrap a paragraph in a panel only when its meaning matches the panel type, so the color always says the same thing:

| Panel           | Use for                                                | Example                                             |
| --------------- | ------------------------------------------------------ | --------------------------------------------------- |
| `panel-info`    | Source and factual context                             | Source panel, Starting point                        |
| `panel-note`    | Something that needs a decision or attention           | "Two visions: decide which one goes first"          |
| `panel-warning` | A risk or caveat                                       | Risk of the proposed phase order; approximate costs |
| `panel-error`   | The problem: what is broken today                      | Problem                                             |
| `panel-success` | A validated fact or closed decision worth highlighting | Evidence confirmed in an interview                  |

One panel per section at most; tables and lists stay outside panels.

Sections in order. Headings stay in English; content in the person's language. Leave a section out when the conversation gives nothing for it, and list it under Open decisions if it matters.

## Source

An H2 heading `Source`, then an info panel with two paragraphs of short sentences, always in this order. No label inside the paragraphs, no status or version line. The first paragraph is the evidence (items 1 and 2); the second starts on a new line and holds the rest (items 3 to 5).

1. **Evidence:** "Este brief parte de [tipo de evidencia] [en/con quién o dónde][; lo que falta]." Never put the person's name in this sentence.
2. **Who provides it:** only when it is someone other than the page author. The live doc's byline already shows the author, so the usual case has no mention. When someone else provided the evidence, add a short sentence of its own that ends with their @mention, so the full display name closes the sentence instead of cutting it: "Lo relata @Name." for secondhand accounts, "Las condujo @Name." for interviews.
3. **Scope:** "El alcance está en el Story Map." (linked). Not in the first version: the `story-map` skill adds it when it creates the board.
4. **Next meeting:** "Siguiente reunión: DATE." with a date node, only if one is scheduled.
5. **Closing:** "Los cambios se consultan en el historial de versiones de Confluence."

```html
<h2>Source</h2>
<div data-type="panel-info">
  <p>
    Este brief parte de la observación propia en cafeterías de San Cristóbal de
    las Casas; todavía no hay entrevistas con dueños.
  </p>
  <p>
    El alcance está en el <a href="WHITEBOARD_URL">Story Map</a>. Siguiente
    reunión: <time datetime="YYYY-MM-DD">YYYY-MM-DD</time>. Los cambios se
    consultan en el historial de versiones de Confluence.
  </p>
</div>
```

## Problem

Two or three sentences in an error panel: who has the problem, what goes wrong, and where it surfaces. The problem, not the solution.

## Primary job

One Jobs to be Done statement in a blockquote: "Cuando [situación], quiero [motivación], para que [resultado]."

## Two visions

Only when stakeholders ask for things of very different size (common in client requests). A note panel saying a decision is needed, then a table: Who | What they asked for | Evidence of the problem.

## Actors and permissions

Table: Actor | Can do | Pain today. Bold the primary user. Permissions matter: who can see what, who can change prices.

## Business rules

Table: Rule | Who defines it | Varies by customer. Rules that vary between customers become per-tenant configuration; say so in one sentence above the table if it applies.

## Current workflow

Numbered steps of how it works today, with the tools used at each step.

## Context

Volume, sizes, number of known customers with the problem.

## Evidence of cost

Bullets. Bold the documented incidents and end each with the conclusion it forces on the design.

## Willingness to pay

Who decides, what they pay today, and any previous purchase or attempt, including why it failed.

## Handoff or integration points

Optional, named after the domain (for example "Operator handoff"). What MVP delivers and what moves to Release 2.

## Quality bar

Acceptance conditions that are not features: money calculations, permissions, consistency rules. Each one testable. If a previous system failed on basics, this section comes from that failure.

## Design principles

Functional principles the person states (for example minimalism as a usability requirement, Kanban for scheduling).

## Proposed phasing

Optional. The consultant's proposed order of phases as a numbered list, with a warning panel for any risk in that order.

## Constraints

Legal, data, infrastructure, or cost constraints (for example health data rules, self-hosting, paid messaging APIs). Bold label per bullet.

## Glossary

The customer's words and what they mean.

## Starting point

An info panel with one paragraph: what already exists (code, data, documents, nothing).

```html
<h2>Starting point</h2>
<div data-type="panel-info"><p>Nada construido: ...</p></div>
```

## Riskiest assumptions

Table: Assumption | Status | Risk, ordered by risk from High to Lower. No number column: rows change in a live doc and numbers go stale. Risk is a status lozenge: High (red), Medium (yellow), Lower (green). Status says what evidence exists, with its source.

## Open decisions

Task list. A checked item records a decision with its date as a date node; an open item is a question still waiting for an answer.
