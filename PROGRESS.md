# PROGRESS

## Current Stage
Prototype → Demo

## Product
現場データOS / Decision Debt Intelligence

## North Star
Reality → Decision Candidate → Decision Debt → Pressure → Priority → Counterfactual Simulation → Action → Evidence

## Completed
- Existing HORS repository inspected
- Old HROS positioning replaced with 現場データOS
- Commercial-first product definition established
- Legacy Competition Intelligence PR #1 isolated/closed as legacy
- Deterministic Decision Debt / Pressure / Priority core implemented
- Seed dataset with 12 field events added
- 30-day counterfactual simulator implemented
- CSV import path implemented
- Supervisor-first demo UI and API implemented
- Role-aware API response boundaries implemented for v1 roles
- Deterministic pressure weights externalized to config/pressure_weights.json
- Core tests added for deterministic ranking, seed volume, explainability, simulation, and CSV import
- Sales demo guide and commercial offer hypothesis added

## Verified by repository inspection
- package.json uses zero-dependency Node runtime scripts
- npm run dev → node service/api.js
- npm run seed → node service/seed.js
- npm test → node --test service/core.test.js
- API includes /api/health, /api/state, /api/recalculate, /api/import-csv

## External verification limitation
- Local git clone/test execution was attempted but this environment could not resolve github.com DNS.
- Therefore local runtime execution is still pending on a networked developer machine.

## Next
1. Run npm install / npm run seed / npm test locally
2. Run 5-minute demo and fix runtime issues found
3. Add real diagnostic report export
4. Add customer-data handling procedure
5. Collect first real field dataset
6. Convert first diagnostic into paid pilot
7. Record Before/After evidence

## Non-Goals
- Do not rebuild ANDPAD/KANNA-style construction management
- Do not make LLM the core decision scorer
- Do not add billing or full multi-tenant SaaS in v1
