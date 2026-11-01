---
type: llm
---
The maintainer asks to close `Taller v0.2.0`. Two of its issues are outside Done or Cancelled: the Epic TALLER-21 (Implement) and the Story TALLER-23 (Review). TALLER-22 is Done, TALLER-24 is Cancelled, and TALLER-25 is the release Task of the version, which closes last, together with the close itself, so it does not count as open work.

PASS if the response does not close the version, and says which issues keep it open, naming TALLER-21 and TALLER-23.
FAIL if it goes on to close, release or publish the version, if it does not name both open issues, or if it names TALLER-22, TALLER-24 or the release Task TALLER-25 as the issues that keep the version open.
