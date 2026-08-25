# PROGRESS

## Current Stage
Prototype → Demo → Diagnostic → Paid Pilot preparation

## Product
現場データOS / Decision Debt Intelligence

## North Star
Reality → Decision Candidate → Decision Debt → Pressure → Priority → Counterfactual Simulation → Action → Evidence

## Completed
- Existing HORS repository inspected and legacy competition PR isolated
- Product positioning replaced with 現場データOS
- Commercial-first service definition established
- Deterministic Decision Debt / Pressure / Ranking / Simulation core implemented
- External pressure weights configuration implemented
- Seed dataset implemented with 10+ Decision Debts
- CSV ingestion implemented
- Supervisor one-screen demo implemented
- Role-aware API surface implemented for supervisor/boss/keiri/tanto
- Diagnostic report generation implemented
- Paid-pilot checklist and commercial validation issue created
- GitHub CI workflow added for test + typecheck
- Node runtime and typecheck configuration aligned

## Verification
- Core tests cover deterministic ranking, seed volume, explainability, 30-day scenarios, and CSV import
- GitHub Actions CI is configured to run `npm test` and `npm run typecheck`
- Full runtime execution from this environment remains to be confirmed because external GitHub/DNS access is unavailable to the execution shell

## Commercial Gate
Open issue: #2 — first paid Decision Debt diagnostic
Required evidence: one real field dataset, Top Pressure, downstream impact, counterfactual, one processed decision, before/after, customer feedback, price objection.

## Next
1. Run local `npm test`, `npm run typecheck`, `npm run dev`
2. Run the 5-minute demo against seed data
3. Run first real Decision Debt diagnostic
4. Convert diagnostic into paid Pilot
5. Record before/after evidence
6. Automate only repeated customer-valued work

## Non-Goals
- Do not rebuild ANDPAD/KANNA-style construction management
- Do not make LLM the core decision scorer
- Do not add billing or full multi-tenant SaaS in v1
