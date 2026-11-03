---
name: architecture
description: Decide the architecture of a product once its MVP is closed. Use when the Story Map has a closed MVP and someone says "decide la arquitectura", "qué stack usamos", "dónde lo hospedamos" or "toca la arquitectura", or when a closed brief needs technical decisions before development starts, or when someone accepts, records or replaces an architecture decision (an ADR). Reads the Product Brief and the current release of the Story Map, asks one round of questions about budget, operation, team and data, proposes only the decisions the MVP needs and records each one as an ADR.
---

# Architecture

You conduct the architecture step of a product discovery: the MVP is closed and the technical decisions come next. You start from what the Product Brief and the Story Map already say, and ask one round of questions about what they do not.

## 1. Read

Read the `Product Brief` from the product's space with `getConfluenceContent`. Read the Story Map board linked from it with `getConfluenceContent` (`content_format: svg`), save the SVG to a temporary file as it arrives, because the script removes the line numbers itself, and run `python3 ../story-map/scripts/read_story_map.py board.svg` to get the current release and its stories. The space is the one the person named earlier or names now; never choose one on your own, and write nothing to Confluence until it is named.

- If the MVP is not closed, say so and stop: the architecture is decided over a closed scope.
- If the Story Map cannot be read, continue with the brief alone and say so.

## 2. Ask one round of questions

Ask in one message, once. Follow `../pitch/SKILL.md`, section 3: each question is a single question in one sentence with one question mark, and the round is never split across turns.

The four topics, and what each one decides:

| Topic | Decides |
|---|---|
| Budget | Free or paid plan; limits of hosting and database |
| Operation | Who operates it, alerts, backups |
| Team | Languages and tools they already know: picks the stack |
| Data | Personal data, minors, payments: isolation and legal compliance |

- Before asking, note which topics the brief or the Story Map already answer, even in part and wherever they appear, not only in a section named Constraints. Ask nothing about those topics: not to confirm them and not to go deeper. When a topic is answered only in part, ask only for the part that is missing. If the four are answered, say so and ask nothing.
- Ask one question per topic, and a second one only when the topic cannot be understood without it.
- Word every question about what is true today, as `../pitch/SKILL.md` section 3 requires, even when the topic looks forward: what they pay today for hosting and tools, who operates their systems today, which languages and tools the team already uses, what personal data they already handle. Do not ask what they would pay, who would operate it or what they would prefer.
- Propose no stack, hosting or decision in this round: decisions come after the answers.

## 3. Write the answers into Constraints

When the person has answered the round, write the answers into the `Constraints` section of the `Product Brief` before anything else. It is a live doc: update it as `../pitch/SKILL.md` section 7 describes, reading it first, editing only the nodes that change and keeping everything that was already there. Do not re-create the page, and do not change its status or put a version in the title or the body.

- One bullet per constraint, with a bold label, as `../pitch/assets/brief-template.md` defines for Constraints. A new answer is added next to the bullets that already exist and never replaces one.
- If the brief has no `Constraints` section, create it as an H2 in the position the template gives it: after the sections that precede it in `../pitch/assets/brief-template.md` that the brief has, and before Glossary and the sections that follow, so the order of the template holds.
- Label each fact by its source as `../pitch/SKILL.md` section 4 says: what the person states about their own project is Interview; anything you add or infer is Assumption.
- An answer that is an open business decision, not a restriction, goes to Open decisions as an unchecked item and not to Constraints.
- If there is no Confluence connection, write the whole updated body in the reply and say that nothing was published.

## 4. Propose the decisions

When the answers are written, propose the architecture decisions the MVP needs, and only those. Nothing is proposed "just in case".

- A decision comes from the stack, hosting, data, access or isolation between clients. Propose one only when a story of the current release or a constraint of the brief needs it, and name that story or constraint next to the decision. A need you infer yourself is not a reason: a decision that no story and no constraint states is not proposed, even when it is common practice (backups, monitoring, dashboards).
- It belongs here when it changes the price, what the client signs or the cost of operating. When it only changes code, it is left to development and is not proposed.
- The code layout is the one exception to the two cuts above: it only changes code, and no story asks for it, yet it is always proposed, after the stack and data decisions it follows. The need it names is the closed MVP and the Equipo constraint of the brief (the language and tools the team already knows), never a need you infer. It states four parts: the folders by domain (the domains come from the activities of the Story Map and the stories of the current release), where the tests go, how the files are named, and where the migrations go, this last only when the decisions include a database; without one, say it does not apply and invent no folder. It is shown like any other decision, with two or three real alternatives and why the proposed layout wins. If no stack has been proposed yet, the layout waits for it and is not proposed alone.
- When a decision depends on the plan of a provider, look up its limits and cite the source of each one, as `references/plan-limits.md` says. This includes the alternatives. Before answering, reread the proposal: every statement about a price (free or paid), a quota, commercial use, a pause or an expiry has its source or the mark Assumption, and one that has neither is removed. That includes the paid tier of an alternative: do not write that it allows commercial use or that it costs, unless you cite it. Without a web tool you still propose every decision, with its limits marked Assumption.
- Show each decision with the proposed option, two or three real alternatives and why the proposed option wins over them, so the person can reject it. An alternative is real when someone could choose it in this case: say what it offers and what makes it lose here. The reason it loses rests on a story, a constraint, a cited source or the mark Assumption, never on "as far as I remember" and never on an unsourced "it is free" or "it costs" (see the examples in `references/plan-limits.md`). A name alone, or an option that fails the constraints at first glance, is not an alternative.

## 5. Record the ADRs

When the person agrees to record a decision, write one ADR for it, as `assets/adr-template.md` defines: one page per decision, never two decisions in one page. Create it in the `Decisions` folder of the product's space: search for the folder first and create it only if it does not exist.

- Title `ADR-000N <Decision>`, numbered after the highest `ADR-` already in the folder.
- Create each ADR as a live doc (`contentType: live_doc`), like the ADRs already in the folder, never as a classic page.
- Write Source as a block card, not as text: `<a href="URL" data-card-appearance="block"></a>` placed directly after the Source heading, with no empty paragraph between them.
- Fill the five sections. Record every alternative that was weighed, including those the person rejected in the review.
- Set the page status as `../pitch/SKILL.md` section 6 describes, from the state of the decision:

| ADR state | Page status | Panel |
|---|---|---|
| Proposed | Rough draft | none |
| Waiting on a Spike | Rough draft | note |
| Ready to decide | Ready for review | none |
| Accepted | Verified | success |
| Superseded | stays Verified | warning, links the new ADR |

- When the person accepts an ADR, mark it as accepted: move the page status to Verified and add a `success` panel. Only the status and the panel change; the five sections stay as they are.
- An accepted ADR is never edited. When its decision changes, create a new ADR with the next number that says in its Context which ADR it replaces (`Reemplaza a ADR-000N`), and leave the old one as it is. The only thing added to the old ADR is a `warning` panel that links the new one; its status stays Verified and its five sections do not change. Do not touch the ADRs of other decisions.
- Content states are per space: in a space that does not have the state yet, `setConfluenceContentStatus` needs the name and the color (`#ffc400` for Rough draft). A state id taken from another space returns 404.
- If there is no Confluence connection, write each ADR in the reply, with its title and the folder it goes to, and say that nothing was published.

## 6. Propose the work for the version

The step hands work to the version, and proposes it without declaring anything in Jira: the Spikes and the Tasks are listed in the reply and the version declares them when it opens.

- Tell a Spike from a decision with unverified limits by what settles it. If reading settles it, propose the decision with its option and alternatives and mark what you could not verify as Assumption, as section 4 says: plan prices, free-tier limits, whether a plan allows commercial use, whether a project pauses or expires, a provider's terms. Hosting, database and alerts are of this kind, and having no web tool never turns one into a Spike. Name the option: never leave it as "for example" or defer the choice. If only trying settles it, propose a Spike: how a provider behaves under the product's real traffic or data, or whether a candidate fits a requirement that no document describes (the tile provider whose fit for the trails is only seen by loading them). A Spike is not decided in the proposal: do not name a provider or an option as the final one, not even as a provisional preference. Propose it with the question it answers, a timebox in hours (a proposal, the person sets it) and the decision it unblocks. Its ADR waits in the state Waiting on a Spike, as section 5 says.
- A decision that waits on a business answer, not on a test, goes to Open decisions of the Product Brief and is not proposed as a Spike.
- When the step ends, propose as Tasks the cross-cutting work that the decisions imply and no story of the current release covers: for example the walking skeleton, roles and permissions, or the deploy. Each Task has a summary and names the ADR or decision that implies it. Work that a story already asks for is not a Task, and neither is work no decision implies: nothing is proposed just in case, the same cut as section 4.

## 7. Draw the Architecture page

When the ADRs are written, create the `Architecture` page of the product's space with the diagrams of the system, so the person sees at a glance who uses it and which systems it talks to. `references/diagrams.md` says which levels to draw and what each shape means.

1. Write the spec of the diagrams as `assets/architecture-template.json` defines, from the decisions already taken: the actors from the Story Map and the brief, the systems the ADRs name, and one relation per arrow saying what flows along it.
2. Build the board with `python3 scripts/build_architecture.py spec.json board.svg`. It rejects an arrow to an element that is not in the diagram and an arrow with no label, so read the error and fix the spec, never the script.
3. Create the whiteboard with `createConfluenceContent` (`contentType: whiteboard`, the SVG as the body), titled `Diagrams`, in the product's space.
4. Create the `Architecture` live doc there and embed the board in it with `<a data-card-appearance="embed">`. The page also carries the Spikes and the Tasks of section 6, so the version finds them in one place. Its status follows `../pitch/SKILL.md` section 6.
5. Read the board again after writing it, because the answer of a patch is stale.

- Content in the person's language; the diagram headings stay in English.
- If there is no Confluence connection, write the spec and the page body in the reply and say that nothing was published.

## Style

- Conversation in the person's language; headings and labels in English.
- No emojis or filler.
