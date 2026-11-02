---
name: architecture
description: Decide the architecture of a product once its MVP is closed. Use when the Story Map has a closed MVP and someone says "decide la arquitectura", "qué stack usamos", "dónde lo hospedamos" or "toca la arquitectura", or when a closed brief needs technical decisions before development starts. Reads the Product Brief and the current release of the Story Map, then asks one round of questions about budget, operation, team and data.
---

# Architecture

You conduct the architecture step of a product discovery: the MVP is closed and the technical decisions come next. You start from what the Product Brief and the Story Map already say, and ask one round of questions about what they do not.

## 1. Read

Read the `Product Brief` from the product's space with `getConfluenceContent`, and the current release of the Story Map with `../story-map/scripts/read_story_map.py`. The space is the one the person named earlier or names now; never choose one on your own, and write nothing to Confluence until it is named.

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

## Style

- Conversation in the person's language; headings and labels in English.
- No emojis or filler.
