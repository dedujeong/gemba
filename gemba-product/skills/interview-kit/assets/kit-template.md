# Interview Kit template

## Panels

Same meaning as in the Product Brief template (`pitch/assets/brief-template.md`): `panel-info` for context, `panel-note` for something that needs attention, `panel-warning` for a risk or caveat. One panel per section at most; lists and tables stay outside panels.

Sections in order. Headings stay in English; content in the person's language. Nothing in this template is content: every goal, rule, question and checklist item comes from the brief's gaps and from what the person says about the meeting. A section with nothing to put in it is left out, except Session plan and Close.

## Meeting panel

No heading. An info panel with one paragraph: the meeting, with whom, the date as a date node and a link to the brief. Leave out what the person has not said; never invent a date or a name.

```html
<div data-type="panel-info">
  <p>
    <strong>Para:</strong> la reunión con PERSONAS el
    <time datetime="YYYY-MM-DD">YYYY-MM-DD</time>. Sale de los huecos del
    <a href="BRIEF_URL">Product Brief</a>.
  </p>
</div>
```

## Goals

An ordered list of what the meeting must leave: two to four items, each one the answer to a gap, ranked by risk (the highest-risk assumption first).

## Before the meeting

Task list of what to arrange or bring: recording permission, material to show, something to observe on arrival. Only what the gaps or the person call for.

## Rules

Bullets for the interviewer during the session.

1. The rule about past facts and real behavior, taken from `pitch` section 3 and translated, not reworded.
2. When someone says "siempre" or "muchas veces" (always, many times), ask for the last concrete case.
3. Any further rule the meeting needs, for example who answers when several people attend.

## Session plan (N minutes)

N is the length the person gave. One H3 per block, `1. Name (M min)`, with the minutes adding up to N. Group the gaps by theme, one block per theme, and order the blocks so that what the others depend on goes first. Under each block an ordered list of questions.

Each question:

- is one sentence with one question mark and asks about something that happened (see Rules);
- ends with the gap it points to, in italics: `<em>Hueco: Assumption, los clientes prefieren WhatsApp.</em>` The kind is Assumption, Secondhand or Open decision, followed by the gap in a few words;
- never asks about a fact the brief labels Interview.

A note panel at the top of a block is allowed when the block has a trap, for example a budget block that must not ask what they would pay.

The last block is always `Close`: actions for the interviewer, not questions (summarize aloud what was learned, agree the date of the next step).

## Questions by role

One H3 per role at the meeting, named by the role (or by the person when the person gave a name). Under each one an ordered list of questions that only that role can answer from experience, shaped like the Session plan questions: one sentence, one question mark, about something that happened, ending with the gap it points to. A role with no gap to ask about is left out.

When attendees hold different visions, each of them gets the same questions about the difference, one list per person, in the same order and with the same wording. Differences between their answers are information, not something to settle in the meeting.

## Observation checklist

Task list of what to watch without asking, taken from the Secondhand facts and the current workflow that can be seen with one's own eyes.

## After the meeting

Ordered list of what happens with the output: the transcript and where it lands, the interviewer's own notes, the update of the brief with each finding under its source label (`pitch` section 7).
