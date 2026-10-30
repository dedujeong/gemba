---
name: interview-kit
description: Prepare a client meeting from the gaps of the Product Brief. Use when a brief already exists and a meeting with the client or users is coming, when someone asks to prepare the meeting, the interview or the questions, or says "se acerca la reunión". Reads the brief, finds what is still an assumption, secondhand or undecided, drafts an interview kit whose every question points to one of those gaps, and writes it as a live doc in the product's space.
---

# Interview kit

The kit is the person's script for a meeting with the client. It does not repeat what the brief already confirmed: it goes after what the brief still does not know.

## 1. Read the brief

Read the `Product Brief` from the product's space with `getConfluenceContent`. The space is the one the person named earlier or names now; never choose one on your own, and write nothing to Confluence until it is named.

Ask once for what the brief cannot tell you and the person has not said: the role each person at the meeting plays (who decides, who operates, who pays), the date and how long the meeting lasts. Names are optional; roles are not. Do not invent any of them. Leave out of the kit what stays unanswered.

Until the roles are known, write no kit, no session plan and no questions: ask and wait. If the person already said who attends and what each does, do not ask again.

## 2. Find the gaps

A gap is what the brief does not yet know from an interview:

- A fact labeled **Assumption**.
- A fact labeled **Secondhand**.
- An **Open decision** still unchecked.

Facts labeled **Interview** are not gaps: do not ask about them again. Rank the gaps by risk, taking the order of Riskiest assumptions when the brief has that section.

If the brief has no gaps, say so and do not draft a kit: there is nothing left to validate with a meeting.

## 3. Draft the kit

Follow `assets/kit-template.md` for the sections, their order and the shape of each question.

- Every question points to one gap and says which one, in the form the template defines. A question that points to no gap is left out, however interesting.
- Word every question under the rule in `../pitch/SKILL.md`, section 3, the paragraph that begins "Ask about the past and real behavior, never opinions". Read it before drafting and apply it as written; do not restate it in other words. The Rules section of the kit carries that rule too, translated.
- Before writing the kit, go through the questions one by one against that rule, in every block and for every person asked. A question in the conditional or the subjunctive ("habría", "sería", "si tuvieran", "would", "if") is a hypothetical even when it sounds like a fact: rewrite it as the last time it happened, or drop it.
- Give each question to the role that can answer it from experience, and do not ask the one who decides what only the one who operates knows. Role-specific questions go under Questions by role in the template.
- When two or more attendees hold different visions, because the brief has Two visions or an open decision about which to follow, ask each of them the same questions about the difference, written separately under each person, so each answers on their own.
- Write only what the brief and the conversation support. Do not carry content over from any other kit.

## 4. Create the live doc

- Find the brief's URL in the space and put it in the meeting panel.
- Create the kit with `createConfluenceContent` (contentType `page`, HTML body), titled `Interview Kit`, in the product's space. Title only by its name, as `pitch` section 2 says. Then convert it with `executeWrite` → `convertConfluenceContentMode` (`targetMode: live_doc`).
- Set the page status to Rough draft right after creating it, as `pitch` section 6 describes. The status replaces any status line in the body, and the body carries no version number.
- Tell the person the kit is a draft to review, and give them the link.

If there is no Confluence connection, write the exact title, body and page status in the reply and say that nothing was published.

## Style

- Conversation in the person's language; headings and labels in English.
- No emojis or filler.
