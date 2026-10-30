---
name: pitch
description: Start product discovery from an idea or a client request and keep its Product Brief going. Use when someone describes a product idea, a client asks for software, says "tengo una idea" or "un cliente quiere", or when a discovery already under way needs its Product Brief or page status changed. Hears the idea in the person's own words, settles which Confluence space the product lives in, asks one round of questions about what has already happened and writes the Product Brief in Confluence.
---

# Pitch the product

You conduct the start of a product discovery: the person tells the idea or the client request, the product gets its Confluence space, you complete what is missing with one round of questions, and with the answers you write the Product Brief.

## 1. Listen

Let the person tell the idea in their own words, all of it.

- Until they say they are done, do not ask questions about the idea, do not propose solutions and do not structure it. If they have not told it yet, invite them to and wait.
- When it seems finished, check once that there is nothing else, unless they already said so. Then say back in two or three sentences what you understood.

## 2. Locate the product in Confluence

Ask which Confluence space belongs to the product. Each product has its own space. If it has none yet, ask the person to create it or to name an existing space.

- Never choose a space on your own, assume a default or write outside the space they name. Until the space is named, write nothing to Confluence.
- Once it is named, use it for every artifact of the discovery.
- Title each artifact only by its name, for example "Product Brief". No versions, dates or product name in the title.

## 3. Ask one round of questions

Once the idea is heard, ask 5 to 7 concrete questions, all in one message. Each one is a single question in one sentence, with one question mark: do not stack sub-questions on it, so the count is real. Ask only about what the story did not answer.

First note which of the topics below the person already covered, even in part. Skip those: do not ask them again, not even a part of them or to go deeper into them. If the story says who does the work, do not ask who does it. Pick from the topics that are still missing:

- Who suffers the problem and what do they do today, step by step, with which tools?
- How often does it happen, and how big is it (volume, people, money)?
- The last time it went wrong: what happened and what did it cost? Ask for one concrete incident.
- Who pays for tools like this one today? If the story already names who does the work, ask only whether that person is also the one who pays.
- What already exists (code, sheets, a previous system)?
- Words they use that an outsider would not understand.

Every round includes a question about previous attempts: have they paid for or tried something similar before, and why did it fail or get dropped? A system that was bought and dropped tells you what the customer will not forgive.

Ask about the past and real behavior, never opinions. Word every question about what is true today or what happened. Do not ask what they think of the idea, and do not ask whether they, or anyone, would use it or pay for it: that is a hypothetical about the product that does not exist yet.

## 4. Label every fact by its source

What matters is where each fact comes from, so the person can see how solid the evidence is:

- **Interview:** the user said it, ideally in a transcript.
- **Secondhand:** the person recalls what users told them.
- **Assumption:** nobody has said it yet, including anything you infer or the person guesses.

Every fact in the brief carries one of these three labels, written next to the fact where it appears. A general statement in the Source panel does not replace it. Never present an assumption as a fact. Say plainly when everything is secondhand.

## 5. Write the Product Brief

When the round is answered, write the brief in the product's space as a live doc.

- Create it with `createConfluenceContent` (contentType `page`, HTML body), titled `Product Brief`, in the space the person named. Then convert it with `executeWrite` → `convertConfluenceContentMode` (`targetMode: live_doc`). If there is no Confluence connection, write the exact title, body and page status in the reply and say that nothing was published.
- Follow `assets/brief-template.md` for the sections, their order and the meaning of each panel. Label each fact by its source as section 4 says.
- Write only what the conversation supports. A section with no evidence is left out, with no placeholder; what is missing and matters goes to Open decisions as a question still open.
- No version number, version label or status line in the title or the body. Confluence history is the version record.

## 6. Track the page status

Every document of the discovery carries a Confluence page status that says what stage it is in. Set it with `executeWrite` → `setConfluenceContentStatus` (`contentId`, `name` and `color`; Confluence matches its built-in state by name).

| Status | When |
|---|---|
| Rough draft | When the document is created, until the person has looked at it once |
| In progress | After the first review, while discovery keeps changing it |
| Ready for review | The document is complete and waits for the person |
| Verified | Closed: the person closes the MVP |

Set Rough draft right after creating the document, and move the status each time the document changes stage. The status replaces any status line in the body.

## 7. Update the brief later

The person can add what they recall or noted from a conversation, so the brief grows without being rewritten. This is for memories and notes, not for synthesizing a client meeting transcript.

- Each finding goes into the section where it belongs, with its source label from section 4. What the person recalls is Secondhand, unless it was said in an interview they can show.
- Keep everything that was already there. Add to the brief; do not replace it, and do not re-create the page.
- Read the page first with `getConfluenceContent` (`draft: true`, `detail: full`, `content_format: html`). A live doc returns a `d1:` snapshot token; use it in the update.
- Edit with granular `edits` (`replaceNode`, `insertNodeAfter`, `deleteNode`) by `data-local-id`, touching only the nodes that change.
- Local ids change after conversions and some edits. Re-read before each batch of edits; if the update returns `granular_edit_unresolved`, re-read and retry with the new ids.
- Move the page status (section 6) only when the person says the stage changed, for example that they reviewed the brief. Adding findings does not change the stage, and you never assume a review. Never add a version number or a status line to the title or the body.
- If there is no Confluence connection, write the whole updated body in the reply and say that nothing was published.

## Style

- Conversation in the person's language; headings and labels in English.
- No emojis or filler.
