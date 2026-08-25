# Public Data Ingestion Layer

Research infrastructure for reproducible public construction-data benchmarks. It is intentionally separated from customer data.

## Pipeline

`official source → retrieval manifest → raw artifact → SHA-256 provenance → normalized benchmark event → benchmark`

## P0 sources

- `mlit_dpf`: current MLIT Data Platform user API
- `estat_construction_orders`: e-Stat construction orders data API/download
- `mlit_ppi`: official procurement outlook, notices, bid/contract results, contract changes and performance information

## Rules

- Current official primary source wins over old articles or mirrors.
- Every downloaded artifact gets URL, retrieval timestamp, publication/update date when available, and SHA-256.
- API keys and credentials stay in environment variables; never commit them.
- Public records are benchmark/context candidates only; they are never treated as customer Decision Debt.
- No customer data is written under this directory.
- Bulk raw datasets stay outside Git; manifests and hashes are tracked.

## Normalization

`normalize.js` converts already-downloaded JSON rows into the public benchmark event contract. Network access and credentials remain outside the normalizer.

Every normalized event carries dataset ID, source URL, retrieval timestamp and artifact SHA-256 provenance. `benchmark-schema.json` defines the contract.

Fixture: `sample-estat-input.json`.

## Planned CLI

```bash
npm run public-data:manifest
npm run public-data:fetch -- --source mlit_dpf
npm run public-data:normalize -- --source mlit_dpf
```

The next commercial-data milestone is one real public artifact → verified manifest → normalized benchmark dataset. Public benchmark output must never be presented as customer-observed evidence.
