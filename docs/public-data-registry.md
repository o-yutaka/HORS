# Public Construction Data Registry

Updated: 2026-08-25

Purpose: build a reproducible public-data benchmark for 現場データOS without mixing public research data with customer data.

## Priority sources

### P0 — MLIT Data Platform
- Official: https://www.mlit.go.jp/tec/content/001901915.pdf
- Provides catalog/search/download plus a user API for data retrieval and scheduled/bulk acquisition.
- Relevant construction content includes basic construction information and related infrastructure data.
- API domain changed in 2026; use the current endpoint and do not hard-code the legacy domain. During FY2026 the old and new endpoints run in parallel through 2027-03-31.
- Use: benchmark source for project metadata/event histories and cross-linking to infrastructure/context data.

### P0 — e-Stat Construction Orders
- Official dataset: 建設工事受注動態統計調査
- Current dataset inventory is updated monthly and the API supports XML/JSON/CSV outputs.
- Useful dimensions include contractor type, work type, prefecture, public/private ordering, and time series.
- API requires an e-Stat application ID; keep credentials outside the repository.
- Use: market/volume priors, regional/work-type baselines, anomaly/context features. Do not treat aggregate statistics as individual decision events.

### P0 — MLIT PPI / procurement records
- Official MLIT procurement pages expose procurement outlooks, bid notices, bid/contract results, contract changes, performance ratings, and low-bid investigation summaries.
- Use: convert public procurement lifecycle milestones into event streams.
- First-class event types:
  - forecast_published
  - notice_published
  - bid_result
  - contract_awarded
  - contract_changed
  - performance_result
  - low_bid_review

### P1 — MLIT official facility/procurement pages
- Use only for sources with stable official URLs and explicit public availability.
- Prefer current primary pages/PDFs over third-party mirrors.

## Event normalization contract

Public records must never be fed directly into Decision Debt. They first enter a separate `public_research` namespace:

```text
source
→ raw artifact
→ source provenance
→ normalized event
→ candidate signal
→ benchmark feature
```

A public record can create a **candidate signal**, not an asserted real customer decision.

Required provenance:
- source_name
- source_url
- retrieved_at
- source_version_or_publication_date
- license_or_usage_note
- raw_artifact_hash

## Customer-data boundary

```text
PUBLIC DATA
  → benchmark / prior / pattern discovery

CUSTOMER DATA
  → paid diagnostic / actual Decision Debt
```

Never mix customer identifiers, documents, or operational notes into public benchmark artifacts.

## First benchmark package

Target three layers:

1. Procurement lifecycle events from MLIT PPI.
2. Construction/project metadata from MLIT Data Platform.
3. Time-series and regional priors from e-Stat.

The benchmark should measure whether deterministic rules can recover useful pressure/order signals without claiming that public administrative data represents a customer's actual decision process.

## Acquisition status

- MLIT Data Platform API capability: verified from current official documentation.
- e-Stat API/output formats: verified from current official dataset pages.
- MLIT procurement lifecycle pages: verified as currently published.
- Automated bulk acquisition: next implementation step.
- API credentials: intentionally not committed.
