# Public Data Ingestion Layer

This directory is research infrastructure for public construction data. It is intentionally separated from customer-data ingestion.

## Pipeline

```text
official source
  → fetch manifest
  → raw artifact hash
  → provenance record
  → normalized event
  → benchmark dataset
```

## Source adapters to implement

- `mlit_dpf`: current MLIT Data Platform user API
- `estat_construction_orders`: e-Stat construction orders/receipts data API or downloadable CSV
- `mlit_ppi`: official procurement outlook, notices, bid/contract results, contract changes, performance results

## Rules

- Current official primary source wins over old articles or mirrors.
- Every downloaded artifact gets URL, retrieval timestamp, publication/update date when available, and SHA-256.
- API keys and credentials stay in environment variables; never commit them.
- Public records become benchmark/event candidates only. They are not treated as customer Decision Debt.
- No customer data is written under this directory.

## Planned CLI

```bash
npm run public-data:manifest
npm run public-data:fetch -- --source mlit_dpf
npm run public-data:normalize -- --source mlit_dpf
```

The first implementation should produce machine-readable manifests without committing bulk raw datasets to Git.
