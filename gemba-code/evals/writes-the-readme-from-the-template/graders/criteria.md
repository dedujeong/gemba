---
type: llm
---
The repository has no README, no code and no files that state commands. The Product Brief of a shop called Taller says, in its Problem, that small garages warn each customer by hand when their next service is due and sometimes forget, that the customer stops coming back on time and the garage loses income; its Primary job says that after a service the owner wants the customer to receive a reminder of the next one; and its actors are the garage owner, who records services and sees whom to remind, and the customer, who receives the reminder. The project language is es-MX. The session cannot write files, so the README is expected as content in the response; saying that nothing was written is correct and is not a failure. The response may also list the other steps of setup (the CLAUDE.md block, the git config, the settings file, the .gitignore); those are not part of the README and are not judged.

The README is the markdown block that starts with the title "Taller". The lines "Requirements:" and "Environment variables:" are labels inside Install and Run, not sections.

PASS if all of these hold:
- the title is "Taller", followed by a one-line description about reminding the customer of the next service;
- the headings of level two are, in this order and in English, "What it is", "Install", "Run", "Test";
- What it is is written in Spanish and uses the brief's problem (garages warn by hand and forget) and its actors;
- no real command, version or variable name appears in Install, Run or Test.

FAIL if any of those does not hold: an extra level-two heading, a real command such as `npm install`, a translated heading, data of the brief missing or invented, or no README in the response.
