# Implementation Phase — Instructions (v1.1)

**Guardrail:** You are in the Implementation phase. Enter this phase **only**
after a human explicitly authorises you to begin executing tasks. Execute tasks
strictly in order, one at a time. After completing a task (code + tests), stop
and wait for the next instruction or hand-off before proceeding. If a task is
unclear or blocked, pause and revise the plan/task board before writing code.
Never guess the context—always re-read the latest `active-implementation.md`,
`active-tasks.md`, and manifest before resuming work.

**Goal:** Deliver the tasks from `active-tasks.md` with tight diffs, full
traceability, and documented verification. Update `active-implementation.md`
after each task.

**Output file to update continuously:** `.spec-dev/active-dev/active-implementation.md`

## Rules

- Work on **one task at a time**. Never mix tasks or run ahead.
- Implement only what the task’s `changes` block describes. If scope changes,
  pause and update the task card first.
- Each task must ship with the tests/docs/telemetry noted in the plan.
- Keep diffs minimal and reversible. Feature flags where appropriate.

## Update Log Format (per completed task)

```
## T-001 — <title>
**When**: <YYYY-MM-DD>
**Change Ref**: <commit SHA/link or short patch note>
**Status**: done | partial | reverted
**Evidence**:
- Tests: <commands/results>
- Manual/QA: <steps taken>
- Telemetry: <metrics/alerts touched>
**Notes**: <follow-ups, risks, memory links>
```

## Execution Loop (per task)

1. Re-read the task card; restate acceptance criteria internally.
2. Confirm the plan/spec still align; if not, stop and update upstream files.
3. Implement the listed changes only. Keep commits focused on the task.
4. Run required tests/QA and capture results.
5. Update docs/telemetry as specified.
6. Append the Update Log entry. Link to any new memory (e.g., `.spec-dev/active-memories/T-XXX`).
7. Run `spec-dev memory T-XXX` (if the file does not exist or needs updates),
   `spec-dev tasks-status T-XXX --set done`, `spec-dev tasks-manifest --rewrite --check`,
   and `spec-dev memories` (add `--ensure` if you need to scaffold missing files).
8. Stop. Await human approval or new instructions before starting the next task.

## Completion Criteria

- Every task in `active-tasks.md` has a matching log entry with evidence.
- Tests/docs/telemetry updates are committed as planned.
- No unplanned file edits; task board reflects reality.
- Agent is in a wait state until the next task is authorized.

**Output location:** `.spec-dev/active-dev/active-implementation.md`
