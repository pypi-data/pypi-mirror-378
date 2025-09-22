# Implementation Phase — Instructions (v1.0)

**Goal:** Execute tasks from `active-tasks.md` in order, with tight diffs and
full traceability. Track progress in `active-implementation.md`.

**Output file to update continuously:** `.spec-dev/active-dev/active-implementation.md`

## Rules

- Implement **one task at a time**. Do not batch unless the task list explicitly
  indicates batching.
- Keep diffs minimal and focused on the task’s **Changes** block.
- Add/extend tests that express the task’s Acceptance checks.
- If the task is impossible as written, STOP, update `active-tasks.md` first.

## Update Log Format (append per completed task)

```
## T-001 — <title>
**When**: 2025-09-20
**Change Ref**: <commit SHA(s) or link>  (if unavailable, put a short patch note)
**Status**: done  # done | partial | reverted
**Notes**: <observations, follow-ups, telemetry added>
```

## Execution Steps (per task)

1. Re-open the task card. Re-state acceptance in your own words (internally).
2. Make only the file changes listed in the `changes` fence. If a file not listed
   must change, STOP and update the task card before proceeding.
3. Add/extend tests and docs referenced by the task.
4. Run tests (if available). If acceptance fails, FIX or roll back and update the task.
5. Append the Update Log entry in `active-implementation.md`.
6. Move to the next task.

## Completion Criteria

- All tasks in `active-tasks.md` show as completed in `active-implementation.md`.
- No stray file edits outside the planned changes.
- Docs updated and telemetry present if planned.

**Output location:** `.spec-dev/active-dev/active-implementation.md`.
