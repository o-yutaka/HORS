/**
 * Convert normalized public events into context features.
 * Public context never becomes customer Decision Debt by itself.
 */
export function buildBenchmarkContext(events) {
  const byWorkType = new Map();
  const byGeography = new Map();
  let total = 0;

  for (const event of events) {
    const value = Number(event.value ?? 0);
    if (!Number.isFinite(value)) continue;
    total += value;
    if (event.work_type) byWorkType.set(event.work_type, (byWorkType.get(event.work_type) ?? 0) + value);
    if (event.geography) byGeography.set(event.geography, (byGeography.get(event.geography) ?? 0) + value);
  }

  return {
    source_kind: 'public_benchmark_context',
    event_count: events.length,
    total_value: total,
    work_type_totals: Object.fromEntries(byWorkType),
    geography_totals: Object.fromEntries(byGeography)
  };
}
