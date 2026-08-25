# PROGRESS

## Current Stage
Prototype → Demo → Diagnostic → Paid Pilot preparation → Public benchmark acquisition

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
- Official public-data registry added for MLIT Data Platform, e-Stat construction orders, and MLIT procurement lifecycle sources
- Public-data ingestion boundary added; raw bulk data is gitignored and provenance manifests are reproducible
- Public-data manifest CLI added
- Public benchmark event schema and deterministic normalizer added
- Public benchmark normalization fixture and test added
- Executable e-Stat artifact downloader added for dataset `000040475580`
- Official e-Stat artifact metadata recorded separately from retrieved artifacts

## Public Data Acquisition Targets
1. MLIT Data Platform user API: project/construction metadata and related infrastructure context
2. e-Stat construction orders: monthly/regional/work-type priors and time-series context
3. MLIT PPI / procurement records: forecast → notice → bid/contract result → contract change → performance events

## Current Verified Public Artifact
- e-Stat dataset: `000040475580`
- Title: 建設工事受注動態統計調査 受注高時系列
- Survey month: 2026-05
- Published: 2026-07-10 14:00 JST
- Official page: https://www.e-stat.go.jp/stat-search/files?stat_infid=000040475580
- Status: officially identified; raw artifact not retrieved in this shell because outbound DNS is restricted

Public records are benchmark/context signals. They are never asserted to be customer Decision Debt.

## Verification
- Core tests cover deterministic ranking, seed volume, explainability, daily 30-day simulation, CSV edge cases, and required headers
- Public-data normalizer test covers deterministic IDs and provenance
- CI executes `npm run verify` (core + public-data tests, syntax checks, manifest generation)
- Full runtime execution from this environment remains unconfirmed because external GitHub/DNS access is unavailable to the execution shell

## Commercial Gate
Open issue: #2 — first paid Decision Debt diagnostic
Required evidence: one real field dataset, Top Pressure, downstream impact, counterfactual, one processed decision, before/after, customer feedback, price objection.

## Next
1. In a network-enabled environment, run `npm run public-data:fetch:estat`
2. Run the provenance manifest and verify SHA-256
3. Convert the retrieved workbook into benchmark JSON rows
4. Run public-data benchmark without mixing customer data
5. Run the 5-minute demo against seed + benchmark context
6. Run first real Decision Debt diagnostic
7. Convert diagnostic into paid Pilot
8. Record before/after evidence as observed customer metrics
9. Automate only repeated customer-valued work

## Non-Goals
- Do not rebuild ANDPAD/KANNA-style construction management
- Do not make LLM the core decision scorer
- Do not add billing or full multi-tenant SaaS in v1
