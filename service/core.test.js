import assert from "node:assert/strict";
import test from "node:test";
import { DEFAULT_WEIGHTS, csvToEvents, processEvents, rankDecisionDebts, simulate30Days } from "./core.js";
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
});

test("30 day simulator has all four scenarios", () => {
  const sim = simulate30Days(seedEvents.map((e, i) => ({ ...e, id: String(i) })));
  assert.deepEqual(sim.map(x => x.key), ["A", "B", "C", "D"]);
});

test("CSV import changes the candidate set", () => {
  const before = processEvents(seedEvents).decisionDebts.length;
  const csv = "date,site_id,event_type,status,note\n2026-08-25,SITE-C,delay,open,新規資材が2日遅延";
  const events = csvToEvents(csv);
  const after = processEvents([...seedEvents, ...events]).decisionDebts.length;
  assert.equal(events.length, 1);
  assert.equal(after, before + 1);
});
