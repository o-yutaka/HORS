import fs from 'node:fs';

/**
 * Normalize a small, already-downloaded public-data artifact into the
 * service's benchmark event contract. No network access and no credentials.
 */
export function normalizeConstructionOrders(rows, provenance) {
  return rows.map((row, index) => ({
    event_id: `public:estat:${provenance.dataset_id}:${index + 1}`,
    source_id: 'estat_construction_orders',
    source_kind: 'public_benchmark',
    observed_at: String(row.observed_at ?? row.date ?? '').trim(),
    geography: String(row.geography ?? row.region ?? '').trim() || null,
    work_type: String(row.work_type ?? row.category ?? '').trim() || null,
    metric: 'construction_orders',
    value: Number(row.value ?? row.orders ?? 0),
    unit: String(row.unit ?? '').trim() || null,
    provenance: {
      dataset_id: provenance.dataset_id,
      source_url: provenance.source_url,
      retrieved_at: provenance.retrieved_at,
      artifact_sha256: provenance.artifact_sha256
    }
  }));
}

export function readJsonRows(path) {
  const parsed = JSON.parse(fs.readFileSync(path, 'utf8'));
  if (!Array.isArray(parsed)) throw new Error('Expected a JSON array');
  return parsed;
}
