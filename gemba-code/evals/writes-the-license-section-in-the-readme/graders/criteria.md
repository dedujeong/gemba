---
type: llm
---
The maintainer chose the Apache-2.0 license for a product called Taller and confirmed the holder "Ana Pérez", the address https://github.com/anaperez and the year 2026. The repository has no README. The session cannot write files, so the README is expected as content in the response.

The README is the markdown block that starts with the title "Taller". The lines "Requirements:" and "Environment variables:" are labels, not sections. Headings of the rest of the response, outside that block (such as a report of the other steps), are not headings of the README. A field to fill written between angle brackets is not a command.

PASS if the README:
- has, as its last level-two heading, "License" in English;
- in that section links the text "Apache License 2.0" (or "Apache-2.0") to the file LICENSE;
- has in that section a sentence about redistributing Taller or a derivative work that mentions keeping the copyright notice and the NOTICE file, with a link to NOTICE; the sentence is expected in Spanish, the language of the project, and the wording "among other conditions" ("entre otras condiciones") is part of it and is fine;
- ends with a copyright line for the year 2026 and the holder Ana Pérez, with the holder name linked to https://github.com/anaperez.

FAIL if the License section is missing, names another license, leaves out the NOTICE sentence, shows a different holder or year, or if there is no README in the response.
