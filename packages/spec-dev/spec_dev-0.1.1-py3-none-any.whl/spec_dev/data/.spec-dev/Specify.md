# Specify Phase — Instructions (v1.0)

**Goal:** Produce `active-spec.md` that fully defines **what** to build and **why**,
without dictating code-level implementation.

**Single output file:** `.spec-dev/active-dev/active-spec.md`

## Steps (in order)

1. **Collect Inputs**
   - If a brief exists (any `/brief`, `/context`, or README notes), summarize it.
   - List assumptions explicitly. If an assumption is critical, mark it with ⚠.

2. **Write the Spec**
   - **1) Purpose & Success** — problem statement, KPIs (measurable).
   - **2) Scope** — in-scope / out-of-scope bullets.
   - **3) Personas & Journeys** — primary persona + top 3 user journeys.
   - **4) User Stories with Acceptance** — 5–15 stories. Use Given/When/Then.
   - **5) Non‑Functional Requirements (NFRs)** — latency budget (e.g., p95 ≤ 250ms),
     availability/SLO, security & privacy constraints, accessibility.
   - **6) Interfaces & Data** — external interfaces (API/CLI/UI), data entities with
     invariants (e.g., “email unique”, “amount ≥ 0”).
   - **7) Edge Cases & Risks** — enumerate and rank by impact × likelihood.
   - **8) Validation Plan & Definition of Done (DoD)** — how we’ll verify outcomes.

3. **Add Readiness Checklist (must be present)**
   - [ ] KPIs are measurable.
   - [ ] Stories each have unambiguous Given/When/Then.
   - [ ] NFR budgets set (perf, reliability, security).
   - [ ] Interfaces & data invariants specified.
   - [ ] Edge cases and risks listed with mitigations.
   - [ ] DoD and validation plan present.

4. **Gate**
   - Append a final line: `Gate: PASS` or `Gate: FAIL + reason`.
   - Proceed to Plan only if **PASS**.

## Style & Constraints

- Keep the whole spec ≤ **2 pages** of tight bullets.
- No technology choices here—those belong to the Plan phase.
- Use ISO dates and identifiers for stories (e.g., `US-REG-01`).

**Output location:** `.spec-dev/active-dev/active-spec.md` (overwrite or create).
