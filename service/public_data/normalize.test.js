import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizeConstructionOrders } from './normalize.js';

test('normalizes public rows with deterministic IDs and provenance', () => {
  const provenance = {
    dataset_id: 'fixture-estat-2026-05',
    source_url: 'https://example.invalid/official',
    retrieved_at: '2026-08-25T00:00:00Z',
    artifact_sha256: 'a'.repeat(64)
  };
  const rows = [{ observed_at: '2026-05', geography: '大阪府', work_type: '建築', value: 123, unit: '百万円' }];
  const out = normalizeConstructionOrders(rows, provenance);
  assert.equal(out[0].event_id, 'public:estat:fixture-estat-2026-05:1');
  assert.equal(out[0].value, 123);
  assert.equal(out[0].provenance.artifact_sha256, 'a'.repeat(64));
});
