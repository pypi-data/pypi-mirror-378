# Plan Phase — Instructions (v1.1)

**Guardrail:** You are in the Plan phase. Translate the approved spec into a
technical approach, then stop for review. Do not create tasks or code yet.

**Goal:** Fill `active-plan.md` with the architecture, module boundaries, risks,
validation, and rollout strategy required to ship the spec safely.

**Single output file:** `.spec-dev/active-dev/active-plan.md`

## Flow

1. **Spec Sync (5 min)**
   - Re-read `active-spec.md`; capture a quick snapshot (problem, success metric).
   - Note any open issues; if critical, log them under **Spec Gaps** before proceeding.

2. **Spec Gaps & Assumptions**
   - Table with columns: `Gap / Proposed Fix / Owner / Status`.
   - Resolve or explicitly mark blockers; halt if the spec needs edits first.

3. **Draft the Plan (30–60 min)**
   - **Architecture Overview** — components, boundaries, responsibilities, owners; include a small diagram or text map.
   - **Key Decisions & Rationale** — trade-offs, rejected alternatives, impact.
   - **Interfaces & Contracts** — API/CLI/event surfaces with request/response examples & error handling.
   - **Data Flow & Storage** — schemas, migrations, retention, indexing, regulatory constraints.
   - **Security & Privacy** — authn/z model, secrets, threat mitigations.
   - **Reliability & Performance** — SLIs/SLOs, perf budgets, back-pressure strategies, test environments.
   - **Observability & Operations** — metrics, logs, traces, dashboards, alerting, runbooks.
   - **Testing & Rollout Strategy** — unit/integration/load testing, staged rollout, feature flags, rollback plan.
   - **Artifacts & References** — diagrams, design docs, relevant memories.

4. **Risks Register**
   - Table: `Risk / Likelihood / Impact / Mitigation / Owner`.
   - Include at least one risk per major section (architecture, data, security, operations).

5. **Readiness Checklist**
   - [ ] Owners and responsibilities assigned for each component.
   - [ ] Dependencies and failure handling identified.
   - [ ] Migration/backwards-compat plan defined (or marked N/A with reason).
   - [ ] Telemetry, alerting, and runbook updates specified.
   - [ ] Security controls tied to identified threats.
   - [ ] Testing and rollout plan documented.
   - [ ] Spec gaps resolved or explicitly tracked with owners.

6. **Gate**
   - Append `Gate: PASS` when every checkbox is satisfied; otherwise use
     `Gate: FAIL — <reason>` and stop.
   - Do not move to Tasks until the plan is reviewed and marked PASS.

**Output location:** `.spec-dev/active-dev/active-plan.md`
