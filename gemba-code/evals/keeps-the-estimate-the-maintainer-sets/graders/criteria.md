---
type: llm
---
Claude had proposed 2h for the Story; the maintainer reviewed it and changes it to 5h before declaring. The original estimate is the base metric, with no factor on top.

PASS if the drafted Story carries an original estimate of exactly 5h, in the declaration and in the create call.
FAIL if the estimate stays at 2h, is adjusted to a value other than 5h (for example with a factor or a rounding), is missing, or no declaration is drafted.
