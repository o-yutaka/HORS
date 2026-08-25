import assert from "node:assert/strict";
import test from "node:test";
import { DEFAULT_WEIGHTS, csvToEvents, processEvents, rankDecisionDebts, simulate30Days, HIGH_PRESSURE_THRESHOLD } from "./core.js";
import { seedEvents } from "./data.js";

test("same input produces identical ranking", () => {
  const a = rankDecisionDebts(seedEvents.map(x => ({ ...x })));
  const b = rankDecisionDebts(seedEvents.map(x => ({ ...x })));
  assert.deepEqual(a, b);
});

test("seed creates at least 10 decision debts", () => {
  const state = processEvents(seedEvents);
  assert.ok(state.decisionDebts.length >= 10);
});

test("top decision has explainable breakdown", () => {
  const top = processEvents(seedEvents).decisionDebts[0];
  assert.equal(top.rank, 1);
  assert.deepEqual(Object.keys(top.breakdown), Object.keys(DEFAULT_WEIGHTS));
  assert.match(top.reason, /日停滞/);
  assert.equal(typeof top.estimated_counterfactual_cost, "number");
});

test("30 day simulator advances daily, preserves deterministic scenarios, and returns valid state", () => {
  const input = seedEvents.map((e, i) => ({ ...e, id: String(i) }));
  const a = simulate30Days(input);
  const b = simulate30Days(input);
  assert.deepEqual(a, b);
  assert.deepEqual(a.map(x => x.key), ["A", "B", "C", "D"]);
  for (const scenario of a) {
    assert.equal(scenario.simulation_days, 30);
    assert.equal(scenario.daily.length, 31);
    assert.equal(scenario.daily[0].day, 0);
    assert.equal(scenario.daily[30].day, 30);
    for (let i = 1; i < scenario.daily.length; i += 1) {
      assert.equal(scenario.daily[i].day, scenario.daily[i - 1].day + 1);
    }
    for (const point of scenario.daily) {
      assert.ok(point.unresolved_count >= 0 && point.unresolved_count <= input.length);
      assert.ok(point.high_pressure_count >= 0 && point.high_pressure_count <= point.unresolved_count);
      assert.ok(point.downstream_block_count >= 0);
      assert.ok(point.estimated_counterfactual_cost >= 0);
    }
    assert.equal(scenario.unresolved_count_30d, scenario.daily[30].unresolved_count);
    assert.equal(scenario.final_high_pressure_count, scenario.daily[30].high_pressure_count);
    assert.equal(scenario.estimated_counterfactual_cost_30d, scenario.daily[30].estimated_counterfactual_cost);
    assert.equal(scenario.downstream_block_count_30d, scenario.daily[30].downstream_block_count);
  }
  assert.ok(a[0].final_high_pressure_count >= 0 && a[0].final_high_pressure_count <= input.length);
  assert.ok(HIGH_PRESSURE_THRESHOLD === 70);
});

test("CSV parser handles quoted commas and changes candidate set", () => {
  const before = processEvents(seedEvents).decisionDebts.length;
  const csv = 'date,site_id,event_type,status,note\n2026-08-25,SITE-C,delay,open,"新規資材,特殊仕様が2日遅延"';
  const events = csvToEvents(csv);
  const after = processEvents([...seedEvents, ...events]).decisionDebts.length;
  assert.equal(events.length, 1);
  assert.equal(events[0].note, "新規資材,特殊仕様が2日遅延");
  assert.equal(after, before + 1);
});

test("CSV parser rejects missing required headers", () => {
  assert.throws(() => csvToEvents("date,site_id,note\n2026-08-25,SITE-C,遅延"), /CSV_HEADER_MISSING/);
});

test("CSV parser rejects unclosed quotes", () => {
  assert.throws(() => csvToEvents('date,site_id,event_type,status,note\n2026-08-25,SITE-C,delay,open,"遅延'), /CSV_UNCLOSED_QUOTE/);
});
