# Tasks Phase — Instructions (v1.1)

**Guardrail:** You are in the Tasks phase. Translate the approved plan into a
task board, then stop. Do not write code or combine tasks. Keep the board
additive—move completed cards to the `Done` section instead of deleting them.

**Goal:** Produce `active-tasks.md` — a precise, finite, independently testable
set of tasks that implements the plan. This becomes the authoritative change plan.

**Single output file:** `.spec-dev/active-dev/active-tasks.md`

## Requirements

- 6–30 tasks. If more than 30, split into milestones or feature flags.
- Each task should take ≤ ~6 hours and own its acceptance criteria.
- Every task must list exact **file paths** and **operations** (add/modify/delete/move) without wildcards.
- Tasks must be independently testable. Use `dependencies` only when blocking is unavoidable.
- One Task ID per task (`T-###`). No duplicates.
- Keep the three sections in `active-tasks.md`: `## Backlog`, `## In Progress`,
  `## Done`. Use the CLI (`spec-dev tasks-move`) to shuffle cards between
  sections as work advances.

## Task Card Format (strict)

Each task is a Markdown section:

```
### T-001 — <short title>

**Why**: <1–2 lines tying back to spec/plan decisions>
**Acceptance (Given/When/Then)**:
- Given …
- When …
- Then …

**Changes**
```changes
<path>: <op> -> <detail> @ <selector>
```

**Dependencies**: [T-000, …] or []
**Estimate**: 3h   **Risk**: medium   **Owner**: agent
**Notes**: <optional clarifications>
```

> The fenced block language tag must be `changes`. One file per line. Be explicit.
> Add `**Status:** pending` immediately under the task header; update via the CLI
> helpers (`spec-dev tasks-status`) instead of editing manually.
> Optional `@ <selector>` scopes the change to a region (e.g. `@ fn:init`,
> `@ mod:service_control`, `@ topic:supervisor`). If omitted, the task claims
> the whole file. The manifest treats uniqueness as `(path, selector)`.

## Flow

1. **Plan Sync** — Review `active-plan.md`; list modules/interfaces that require tasks.
2. **Slice Tasks** — Break work into 6–30 slices covering all plan sections.
   - Group tasks by capability or feature flag if helpful.
   - Combine only when changes cannot be tested independently.
3. **Draft Task Cards** — Append new cards under `## Backlog`. Mention tests/docs in Changes.
4. **Order & Dependencies** — Arrange in logical execution order; use
   `spec-dev tasks-status T-### --set <pending|in-progress|done>` instead of
   editing by hand when status changes.
5. **Generate Coverage** — Run `spec-dev tasks-manifest --auto-scope --rewrite --check` to regenerate `active-dev/file-coverage.json` and ensure every `(path, selector)` maps to exactly one task.
6. **Sanity Pass** — Re-read for ambiguity, overlapping files, or missing acceptance.
   If you resume this phase later, re-open the existing board and manifest instead
   of guessing or recreating cards.

## Readiness Checklist
- [ ] Each task has at least one Given/When/Then acceptance bullet.
- [ ] Every file to be touched appears in a `changes` block and the manifest (`spec-dev tasks-manifest --check`).
- [ ] No task exceeds ~6h and each has an Owner.
- [ ] No ambiguous paths or wildcards.
- [ ] Dependencies are minimal and non-circular.
- [ ] Tasks reference relevant spec/plan sections where needed.

## Gate
- End the file with `Gate: READY FOR IMPLEMENTATION` only when all checks pass.
- If any item is missing, leave the gate unset and pause for review.
- After the gate is marked READY, stop and wait for human approval before
  entering the Implementation phase.

**Output location:** `.spec-dev/active-dev/active-tasks.md`
