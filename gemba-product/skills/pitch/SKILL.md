---
name: pitch
description: Start product discovery from an idea or a client request. Use when someone describes a product idea, a client asks for software, or says "tengo una idea" or "un cliente quiere". Hears the idea in the person's own words, settles which Confluence space the product lives in and asks one round of questions about what has already happened and, once they are answered, writes the Product Brief in Confluence.
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

## 4. Write the Product Brief

When the round is answered, write the brief in the product's space as a live doc.

- Create it with `createConfluenceContent` (contentType `page`, HTML body), titled `Product Brief`, in the space the person named. Then convert it with `executeWrite` → `convertConfluenceContentMode` (`targetMode: live_doc`). If there is no Confluence connection, write the exact title and body in the reply and say that nothing was published.
- Follow `assets/brief-template.md` for the sections, their order and the meaning of each panel.
- Write only what the conversation supports. A section with no evidence is left out, with no placeholder; what is missing and matters goes to Open decisions as a question still open.
- No version number, version label or status line in the title or the body. Confluence history is the version record.

## Style

- Conversation in the person's language; headings and labels in English.
- No emojis or filler.
