import test from 'node:test';
import assert from 'node:assert/strict';
import { buildBenchmarkContext } from './benchmark-context.js';

test('benchmark context aggregates public events deterministically', () => {
  const events = [
    { value: 100, work_type: '建築', geography: '大阪府' },
    { value: 50, work_type: '建築', geography: '大阪府' },
    { value: 25, work_type: '土木', geography: '東京都' }
  ];
  assert.deepEqual(buildBenchmarkContext(events), {
    source_kind: 'public_benchmark_context',
    event_count: 3,
    total_value: 175,
    work_type_totals: { '建築': 150, '土木': 25 },
    geography_totals: { '大阪府': 150, '東京都': 25 }
  });
});
