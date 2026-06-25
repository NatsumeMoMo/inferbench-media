# AGENTS.md

This repository uses the Project Memory Protocol.

Before making any code changes, always read:

1. `.ai-dev/README.md`
2. `.ai-dev/RULES.md`
3. `.ai-dev/current/active.md`
4. `.ai-dev/implemented/index.md`
5. `.ai-dev/discussions/index.md`

<!-- PROJECT_MEMORY_PROTOCOL_START -->

## Project Memory Protocol

- Do not treat discussion notes as implemented facts.
- Do not mark any feature or bugfix as completed until the user explicitly accepts it.
- If `.ai-dev/current/active.md` is non-empty, continue the current task unless the user explicitly starts an interrupting bugfix or iteration.
- Every meaningful code change should correspond to a Git commit.
- Every Git commit made during a task must be recorded in `.ai-dev/current/active.md`.
- When the user accepts a task, migrate the final summary to `.ai-dev/implemented/features/`, update `.ai-dev/implemented/index.md`, then clear `.ai-dev/current/active.md`.
- If a new urgent task interrupts an unfinished task, move the current `active.md` into `.ai-dev/current/stash/`, then create a new `active.md` for the interrupting task.
- Before handing off to another Agent, generate a handoff summary using `.ai-dev/templates/handoff.md`.

## Default Behavior

If the user asks to continue development, first summarize the current task state from `.ai-dev/current/active.md`.

If the user asks to implement a previously discussed idea, first locate the relevant proposal in `.ai-dev/discussions/index.md`.

If the user asks to fix or iterate a previous feature, first locate the relevant implemented record in `.ai-dev/implemented/index.md`.

<!-- PROJECT_MEMORY_PROTOCOL_END -->
