# Current Task Stash

This directory stores interrupted active tasks.

Use it only when the user explicitly interrupts the current task with another urgent bugfix, iteration, or feature. Move the full `current/active.md` contents into a named stash file such as `FEATURE-0001-short-title.md`, then create a new `active.md` for the interrupting task.

When the interrupting task is accepted, restore the stashed task by moving it back to `current/active.md`, checking the branch and commit state, and continuing from its `Next Step`.
