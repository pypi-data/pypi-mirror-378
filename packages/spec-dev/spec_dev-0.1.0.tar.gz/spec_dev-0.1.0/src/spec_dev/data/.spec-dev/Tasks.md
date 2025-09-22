# Tasks Phase — Instructions (v1.0)

**Goal:** Produce `active-tasks.md` — a precise, finite list of independently
testable tasks that implement the Plan. This is the authoritative change plan.

**Single output file:** `.spec-dev/active-dev/active-tasks.md`

## Requirements

- 6–30 tasks. If more than 30, split by milestone.
- Each task MUST be implementable within ~6 hours and have its own acceptance.
- Every task lists exact **file paths** and **operations** (add/modify/delete/move).
- No wildcard paths. Be explicit.
- Each task stands alone (independent testability). Use `dependencies` if needed.

## Task Card Format (strict)

Each task is a Markdown section with this structure:

```
### T-001 — <short title>

**Why**: <1–2 lines linking to spec & plan sections>
**Acceptance (Given/When/Then)**:
- Given ...
- When ...
- Then ...

**Changes**
```changes
# One directive per line: <path>: <op> -> <detail>
# op ∈ {add, modify, delete, move}
api/users.ts: modify -> add POST /register handler
api/services/user.service.ts: modify -> new createUser(email) flow
tests/api/users.register.spec.ts: add -> new happy/invalid cases
docs/api/users.md: modify -> document 201/400 responses
```

**Dependencies**: [T-000, …] or []
**Estimate**: 3h   **Risk**: medium   **Owner**: agent
**Notes**: <optional clarifications>
```

> The fenced block language tag **must be `changes`**. Do not use globs. One file per line.

## Steps (in order)

1. Read `active-plan.md`. Extract modules/interfaces into 6–30 tasks.
2. Write tasks in execution order. Use dependencies only when necessary.
3. Add a **File Coverage** section at the bottom listing all files referenced,
   ensuring there are no accidental omissions or collisions.

## Readiness Checklist
- [ ] Each task has at least one acceptance check.
- [ ] Every file to be touched appears in at least one task.
- [ ] No task exceeds ~6h estimate.
- [ ] No ambiguous file path or wildcard.
- [ ] No circular dependencies.

## Gate
- End the file with `Gate: READY FOR IMPLEMENTATION` **only** when all checks pass.

**Output location:** `.spec-dev/active-dev/active-tasks.md`.
