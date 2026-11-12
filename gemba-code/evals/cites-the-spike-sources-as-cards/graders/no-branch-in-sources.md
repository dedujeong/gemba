---
type: regex
pattern: 'Sources\s*</h[1-6]>(?:(?!spike/TALLER-50|\.claude/worktrees/|TALLER-50-can-we-send|<h[1-6])[\s\S])*(?:<h[1-6]|$)'
target: last_message
---
The Sources section of the findings page does not cite the Spike's branch or its worktree.
