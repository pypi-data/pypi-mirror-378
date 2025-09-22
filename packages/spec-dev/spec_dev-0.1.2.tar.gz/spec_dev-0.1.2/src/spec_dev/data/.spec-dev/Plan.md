# Plan Phase — Instructions (v1.0)

**Goal:** Produce `active-plan.md` that defines **how** to build the spec:
architecture, module boundaries, data flow, risks, and validation strategy.

**Single output file:** `.spec-dev/active-dev/active-plan.md`

## Steps (in order)

1. **Inputs**
   - Read `active-spec.md`. If anything is inconsistent or missing, stop and
     propose exact spec edits inside `active-plan.md` under **Spec Gaps**.

2. **Write the Plan**
   - **1) Architecture** — modules/components, responsibilities, boundaries.
     Include a short text diagram.
   - **2) Decisions & Rationale** — list key choices and 1‑line rationale each.
   - **3) Interfaces & Contracts** — public APIs/CLIs/events with request/response
     shapes or signatures (brief, not verbose).
   - **4) Data Flow & Storage** — schemas, indexes, migrations, retention.
   - **5) Security & Privacy** — threats, authn/authz model, secrets handling.
   - **6) Reliability & Performance** — SLIs/SLOs, perf budgets, back-pressure.
   - **7) Observability & Operations** — logs, metrics, traces, dashboards, runbooks.
   - **8) Delivery Strategy** — milestones, cutover/rollback, flags.

3. **Risks**
   - Table of risks with mitigation and owner (can be “agent” for now).

4. **Readiness Checklist**
   - [ ] All components have clear owners/responsibilities.
   - [ ] Every external dependency identified with failure handling.
   - [ ] Backwards compatibility / data migration plan present (if applicable).
   - [ ] Telemetry and runbook defined.
   - [ ] Security controls mapped to threats.

5. **Gate**
   - Append `Gate: PASS` or `Gate: FAIL + reason`.

**Output location:** `.spec-dev/active-dev/active-plan.md`.
