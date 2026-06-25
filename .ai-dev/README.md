# Project Memory

This directory stores project-local memory for AI-assisted development.

It separates project information into three domains:

1. `current/`
   The current active task. This is the most important context for continuation.

2. `implemented/`
   Completed and user-accepted facts. These are already implemented.

3. `discussions/`
   Future ideas, plans, proposals, and discarded options. These are not implemented facts.

4. `events/`
   Append-only event log for important development events.

The Agent should use progressive disclosure:

- Read indexes first.
- Read detailed records only when relevant.
- Never load all historical files by default.
