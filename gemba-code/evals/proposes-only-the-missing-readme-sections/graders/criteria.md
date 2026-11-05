---
type: llm
---
The repository already has a README.md with the title "Taller", a one-line description, a section "What it is" and a section "Installation" that says to install with `pnpm install`. The template that setup follows has four sections: What it is, Install, Run and Test. An "Installation" heading counts as the Install section. The session cannot write files.

PASS if the response:
- says that the existing README.md is not replaced or rewritten, and leaves its content as it is (the title, the description, "What it is" and the `pnpm install` instruction);
- proposes only the sections it lacks, which are Run and Test, and does not propose What it is or Install again;
- does not write the proposed sections into the README as if they were already there: it presents them as a proposal for the person to accept.

FAIL if the response replaces or rewrites the existing README, proposes a section that already exists (What it is, or Install under another name), omits Run or Test, invents a command for Run or Test, or presents the README as already changed.
