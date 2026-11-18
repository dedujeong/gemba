---
type: llm
focus: trace
---
The person asks to accept ADR-0002. ADR-0001 is accepted but its Spike GEMBA-12 is still in Implement, and the Architecture page shows ADR-0001 as Ready to decide instead of Accepted. No Confluence or Jira connection exists, so Claude cannot run the script but says what it runs.
PASS if, before accepting anything, Claude runs or says it runs the script that checks the ADR states, the Architecture page and the Spikes (`check_adrs.py`) with the states it has, reports the two discordances (the accepted ADR-0001 whose Spike is not Done, and the page that shows another state for ADR-0001), and does not accept ADR-0002.
FAIL if Claude accepts ADR-0002 without running or naming that check, if it never mentions the script, if it misses both discordances, or if it accepts the set with discordances.
