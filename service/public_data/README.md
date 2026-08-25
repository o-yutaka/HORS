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

## e-Stat first artifact

The first official target is the `2026-05` “受注高時系列” file, `stat_infid=000040475580`, published 2026-07-10 14:00 JST by the Ministry of Land, Infrastructure, Transport and Tourism. The official page exposes an Excel download and an API interface requiring an application ID. citeturn776310view0

Run:

```bash
npm run public-data:fetch:estat
```

The downloader starts from the official dataset page, discovers the current Excel URL from that page, saves the raw artifact under `service/runtime/public_data/`, and emits `provenance.json` with retrieval time, source URL, resolved download URL, byte size and SHA-256. Raw artifacts are gitignored.

The current environment used for development has outbound DNS restrictions, so retrieval itself must be executed from a network-enabled development/CI environment. The implementation does not fabricate a fallback artifact.

## Normalization

`normalize.js` converts already-downloaded JSON rows into the public benchmark event contract. Network access and credentials remain outside the normalizer.

Every normalized event carries dataset ID, source URL, retrieval timestamp and artifact SHA-256 provenance. `benchmark-schema.json` defines the contract.

Fixture: `sample-estat-input.json`.

The next commercial-data milestone is one real public artifact → verified manifest → normalized benchmark dataset. Public benchmark output must never be presented as customer-observed evidence.
