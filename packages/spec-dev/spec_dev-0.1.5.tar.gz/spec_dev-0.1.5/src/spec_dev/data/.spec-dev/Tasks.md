# Tasks Phase — Instructions (v1.1)

**Guardrail:** You are in the Tasks phase. Translate the approved plan into a
task board, then stop. Do not write code or combine tasks.

**Goal:** Produce `active-tasks.md` — a precise, finite, independently testable
set of tasks that implements the plan. This becomes the authoritative change plan.

**Single output file:** `.spec-dev/active-dev/active-tasks.md`

## Requirements

- 6–30 tasks. If more than 30, split into milestones or feature flags.
- Each task should take ≤ ~6 hours and own its acceptance criteria.
- Every task must list exact **file paths** and **operations** (add/modify/delete/move) without wildcards.
- Tasks must be independently testable. Use `dependencies` only when blocking is unavoidable.
- One Task ID per task (`T-###`). No duplicates.

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
<path>: <op> -> <detail>
```

**Dependencies**: [T-000, …] or []
**Estimate**: 3h   **Risk**: medium   **Owner**: agent
**Notes**: <optional clarifications>
```

> The fenced block language tag must be `changes`. One file per line. Be explicit.

## Flow

1. **Plan Sync** — Review `active-plan.md`; list modules/interfaces that require tasks.
2. **Slice Tasks** — Break work into 6–30 slices covering all plan sections.
   - Group tasks by capability or feature flag if helpful.
   - Combine only when changes cannot be tested independently.
3. **Draft Task Cards** — Follow the strict format. Mention tests/docs in Changes.
4. **Order & Dependencies** — Arrange in logical execution order; add dependency lists sparingly.
5. **File Coverage** — Add a section at the bottom enumerating every file touched across tasks; ensure no file appears without a task.
6. **Sanity Pass** — Re-read for ambiguity, overlapping files, or missing acceptance.

## Readiness Checklist
- [ ] Each task has at least one Given/When/Then acceptance bullet.
- [ ] Every file to be touched appears in a `changes` block and the File Coverage list.
- [ ] No task exceeds ~6h and each has an Owner.
- [ ] No ambiguous paths or wildcards.
- [ ] Dependencies are minimal and non-circular.
- [ ] Tasks reference relevant spec/plan sections where needed.

## Gate
- End the file with `Gate: READY FOR IMPLEMENTATION` only when all checks pass.
- If any item is missing, leave the gate unset and pause for review.

**Output location:** `.spec-dev/active-dev/active-tasks.md`
