# PROGRESS

## Current Stage
Prototype → Demo → Diagnostic → Paid Pilot preparation

## Product
現場データOS / Decision Debt Accounting

## North Star
Reality → Decision Candidate → Decision Debt → Pressure → Priority → Counterfactual Simulation → Action → Evidence

## Completed
- Existing HORS repository inspected and legacy competition PR isolated
- Product positioning replaced with 現場データOS
- Commercial-first service definition established
- Deterministic Decision Debt / Pressure / Ranking core implemented
- Decision Debt estimated counterfactual cost explicitly separated from observed outcomes
- External pressure weights configuration implemented
- Seed dataset implemented with 10+ Decision Debts
- Deterministic 30-day simulation implemented with daily progression
- Robust quoted CSV ingestion and required-header validation implemented
- Supervisor one-screen demo implemented
- Role-aware API surface implemented with dev-role header scope and endpoint permissions
- Diagnostic report generation implemented with engine/version/config provenance
- Diagnostic report now exposes Top1/Top3 counterfactual deltas
- Paid-pilot checklist and commercial validation issue #2 created
- GitHub CI workflow aligned with zero-dependency `npm run verify`
- Verification tests expanded for simulation determinism, CSV edge cases, and estimate semantics
- Competitive positioning refined around Decision Debt Accounting / 判断負債会計

## Verification
- Core tests cover deterministic ranking, seed volume, explainability, daily 30-day simulation, CSV edge cases, and required headers
- CI executes `npm run verify` (tests + Node syntax checks)
- Full runtime execution from this environment remains unconfirmed because external GitHub/DNS access is unavailable to the execution shell

## Commercial Gate
Open issue: #2 — first paid Decision Debt diagnostic
Required evidence: one real field dataset, Top Pressure, downstream impact, counterfactual, one processed decision, before/after, customer feedback, price objection.

## Next
1. Run local `npm run verify` and `npm run dev`
2. Run the 5-minute demo against seed data
3. Run first real Decision Debt diagnostic
4. Convert diagnostic into paid Pilot
5. Record before/after evidence as observed customer metrics
6. Automate only repeated customer-valued work

## Non-Goals
- Do not rebuild ANDPAD/KANNA-style construction management
- Do not make LLM the core decision scorer
- Do not add billing or full multi-tenant SaaS in v1
