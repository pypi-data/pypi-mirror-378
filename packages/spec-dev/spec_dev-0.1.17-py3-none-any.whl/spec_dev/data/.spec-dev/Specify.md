# Specify Phase — Instructions (v1.1)

**Guardrail:** You are in the Specify phase. Produce the spec, stop, and wait for
review before writing plans, tasks, or code.

**Goal:** Fill in `active-spec.md` so the team understands **what** to build and
**why**, aligned to the user’s request.

**Single output file:** `.spec-dev/active-dev/active-spec.md`

## Flow

1. **Kickoff Sync (5 min)**
   - Restate the request in 1–2 bullets (problem, desired outcome, success clue).
   - Note any unknowns or external dependencies as “Open Questions”.
   - If anything blocks progress, stop and surface the question instead of guessing.

2. **Collect Inputs (5–10 min)**
   - Mine briefs, README/context notes, existing memories, and recent commits.
   - Capture explicit assumptions; mark risky ones with ⚠.

3. **Draft the Spec (20–40 min)**
   - **Purpose & Success** — problem, KPIs/OKRs or measurable signals.
   - **Scope** — bullets for in-scope vs. out-of-scope.
   - **Personas & Journeys** — up to 3 personas and their critical flows.
   - **User Stories (Given/When/Then)** — enough stories to cover the happy path,
     key edge cases, and supporting roles.
   - **NFRs** — performance, reliability/SLO, security/privacy, accessibility.
   - **Interfaces & Data** — external touchpoints (APIs, UI, events) plus data
     invariants.
   - **Edge Cases & Risks** — ranked by impact × likelihood with mitigation notes.
   - **Validation Plan & Definition of Done** — tests, telemetry, manual QA, rollout.
   - Link to any prior specs or memories you rely on.

4. **Readiness Checklist**
   - [ ] KPIs are measurable.
   - [ ] Stories each have unambiguous Given/When/Then.
   - [ ] NFR budgets set (perf, reliability, security, accessibility).
   - [ ] Interfaces & data invariants specified.
   - [ ] Edge cases and risks listed with mitigations.
   - [ ] DoD and validation plan present.
   - [ ] Open questions (if any) are documented explicitly.

5. **Gate**
   - Append `Gate: PASS` when every box is checked. Otherwise append
     `Gate: FAIL — <reason>` and stop here.
   - Do **not** move to Plan until the spec is reviewed and marked PASS.

## Style Guidance

- Target ≤ 2 pages of crisp bullets; use numbered lists for flows.
- Stick to product/behavior language. Leave implementation decisions for the
  Plan phase.
- Use ISO dates and stable identifiers for stories (e.g., `US-GEN-01`).

**Output location:** `.spec-dev/active-dev/active-spec.md`
