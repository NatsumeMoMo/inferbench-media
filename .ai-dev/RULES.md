# Project Memory v0 Protocol

## 1. Overall Principles

v0 does not use a database, vector index, MCP server, or complex CLI.

v0 does three things:

1. Use `AGENTS.md` as the agent startup entry point.
2. Use `.ai-dev/` to store project memory, current state, implemented records, and discussion records.
3. Use Git commit hashes to bind memory records to real code changes.

Core responsibilities:

```text
AGENTS.md = Agent startup entry point
.ai-dev/RULES.md = Project memory system rules
.ai-dev/current/active.md = Current task state
.ai-dev/implemented/ = Accepted facts that already happened
.ai-dev/discussions/ = Discussions that have not happened as implementation
Git = Real code change history
```

## 2. Information Domains

Project memory has three domains:

```text
current = what is happening now
implemented = facts that happened and were accepted by the user
discussions = possible future work that may never happen
```

Agents must follow these boundaries:

1. `current` is not long-term history.
2. `implemented` is not a planning area.
3. `discussions` is not a fact area.
4. Git commits record how code changed.
5. `.ai-dev` records why code changed, current progress, and user acceptance state.

## 3. Single Active Task

Only one active task may exist at a time:

```text
.ai-dev/current/active.md
```

The file must be either empty or describe one task. Do not describe multiple features, bugfixes, or iterations in one `active.md`.

If an interrupting task arrives, stash the current task before creating the new active task.

## 4. Task Types

Allowed task types:

```text
FEATURE
BUGFIX
ITERATION
REFACTOR
RESEARCH_SPIKE
DOC_UPDATE
```

Meanings:

```text
FEATURE = new functionality
BUGFIX = error fix
ITERATION = improvement to existing functionality
REFACTOR = structure change without intended behavior change
RESEARCH_SPIKE = exploratory experiment
DOC_UPDATE = documentation change
```

## 5. Task Status

Current task statuses:

```text
ACTIVE
AWAITING_USER_ACCEPTANCE
INTERRUPTED
COMPLETED_PENDING_MIGRATION
```

Important rules:

- Code being changed by an agent does not mean the task is complete.
- A task is complete only after explicit user acceptance.
- Before user acceptance, the furthest status is `AWAITING_USER_ACCEPTANCE`.

## 6. Task ID Rules

Use simple increasing IDs:

```text
FEATURE-0001
BUGFIX-0001
ITERATION-0001
REFACTOR-0001
DOC-0001
RESEARCH-0001
IDEA-0001
```

`IDEA` is only for discussion records. It does not represent implementation.

## 7. Starting A New Task

Before starting a new task, read:

```text
.ai-dev/current/active.md
```

If it is empty, a new task may begin.

If it is not empty, determine whether the user wants to continue the current task or explicitly interrupt it with a bugfix or iteration.

If the user does not clearly request an interruption, continue the current task.

When starting a task, write:

```text
Task ID
Task Type
Status
Branch
Started At
Base Commit
Goal
User Requirements
Acceptance Criteria
Next Step
```

## 8. Normal Development Rules

After each meaningful code change, the agent should:

1. Inspect changes with `git diff`.
2. Run required tests or builds.
3. Create a Git commit.
4. Record the commit hash in `active.md`.
5. Update `Files Touched`.
6. Update `Current Implementation Summary`.
7. Update `Next Step`.

v0 does not require a commit for every tiny line edit, but meaningful stages must be committed.

Recommended commit messages:

```text
FEATURE-0001: add initial CLI skeleton
BUGFIX-0001: fix cmake target include path
ITERATION-0001: refine benchmark result schema
```

## 9. User Acceptance Rules

After implementation, the agent may only move the task to:

```text
AWAITING_USER_ACCEPTANCE
```

Do not mark it completed directly.

Acceptance requires explicit user intent such as:

```text
ok
accepted
passed
no problem
ship it
acceptance passed
this feature is complete
```

After user acceptance, the agent may:

1. Finalize `active.md`.
2. Generate `implemented/features/TASK-ID-title.md`.
3. Update `implemented/index.md`.
4. Record the final commit.
5. Move related discussions to `discussions/archived/` when applicable.
6. Clear `current/active.md`.

## 10. Agent Finished But User Has Not Accepted

If the agent believes the implementation is finished but the user has not accepted it:

```text
active.md must remain.
Status = AWAITING_USER_ACCEPTANCE.
```

Do not migrate it to `implemented`.
Do not clear `active.md`.
Do not mark related discussion content as implemented.

## 11. Acceptance Rejected

If the user asks for changes, acceptance did not pass.

Then:

```text
Status returns to ACTIVE.
Work continues under the same Task ID.
New commits are appended to WIP Commits.
```

Do not create a new feature ID unless the user clearly says this is a separate feature.

## 12. Interrupting Task Rules

If `active.md` is non-empty and the user explicitly asks for an urgent bugfix or feature iteration:

1. Move `active.md` to `current/stash/TASK-ID-title.md`.
2. Record `task_stashed` in `events.jsonl`.
3. Create a new `active.md`.
4. After the new task is completed and accepted, clear `active.md`.
5. Restore the original task from stash.

Interruptions must be explicit. Example phrases:

```text
pause this and fix xxx first
put the current feature aside
insert a bugfix
handle another issue first
```

## 13. Restoring A Stashed Task

When restoring a stashed task:

1. Move it from `current/stash/` back to `active.md`.
2. Check the related branch and commit state.
3. Summarize the restored current state.
4. Continue from `Next Step`.

Do not lose original WIP commits, files touched, or open questions.

## 14. Discussion Records

Discussion records store possible future work only.

Suitable discussion content:

```text
future feature ideas
technical route discussions
architecture proposals
possibly discarded options
undecided plans
future version roadmap
```

Not suitable:

```text
implemented and accepted features
current detailed task state
per-commit logs
```

When a discussion is implemented:

1. Reference the discussion in the implemented record.
2. Move the proposal from `discussions/proposals/` to `discussions/archived/`.
3. Update `discussions/index.md` to `IMPLEMENTED` or remove it from the active list.

## 15. Implemented Records

`implemented` stores only user-accepted facts.

Each implemented record must include:

```text
what was finally implemented
final behavior
files changed
final commit
key design decisions
related discussions
known limitations
```

Forbidden:

```text
writing unaccepted work into implemented
writing future plans as completed facts
treating discussion records as facts
```

## 16. Git Rules

v0 recommends:

```text
one task per branch
one meaningful stage per WIP commit
after user acceptance, squash to one final commit if desired
implemented records only record the final commit
active.md may record WIP commits
```

Branch naming:

```text
feature/FEATURE-0001-short-title
bugfix/BUGFIX-0001-short-title
```

After acceptance:

```text
main keeps the final squash commit.
```

If WIP commits are no longer reachable after squash, `implemented` records only the final commit. WIP process notes can remain in `events.jsonl` or the migrated active record.

## 17. Handoff Rules

Any agent taking over must first read:

```text
AGENTS.md
.ai-dev/README.md
.ai-dev/RULES.md
.ai-dev/current/active.md
.ai-dev/implemented/index.md
.ai-dev/discussions/index.md
```

Then produce a handoff summary:

```text
current task
current status
whether the user accepted it
files already changed
latest commit
next step
whether stashed tasks exist
relevant discussion or implemented background
```
