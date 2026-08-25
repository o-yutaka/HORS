import { PRESSURE_WEIGHTS } from "./config.js";

export const DEFAULT_WEIGHTS = PRESSURE_WEIGHTS;
const clamp = (n, min = 0, max = 100) => Math.max(min, Math.min(max, n));

export function normalizeEvent(event, index = 0) {
  return {
    id: String(event.id ?? `EV-${String(index + 1).padStart(4, "0")}`),
    site_id: String(event.site_id ?? "SITE-001"),
    date: String(event.date ?? "1970-01-01"),
    event_type: String(event.event_type ?? "unknown"),
    status: String(event.status ?? "open"),
    note: String(event.note ?? "")
  };
}

export function extractDecisionCandidates(events) {
  const list = events.map((e, i) => normalizeEvent(e, i));
  return list
    .filter((e) => /delay|遅れ|遅延|未承認|承認待|未決|不足|未着|stop|停止|hold|pending/i.test(`${e.event_type} ${e.note}`))
    .map((e, i) => ({
      id: `D-${String(i + 1).padStart(3, "0")}`,
      site_id: e.site_id,
      title: inferTitle(e),
      owner_role: "supervisor",
      decision_state: "open",
      blocked_state: "blocked",
      constraint_reason: e.note || e.event_type,
      delay_days: inferDelay(e),
      impact_cost: inferCost(e),
      downstream_block_count: inferDownstream(e),
      dependency_depth: inferDepth(e),
      first_blocked_at: e.date,
      last_state_change_at: e.date,
      uncertainty_score: inferUncertainty(e),
      counterfactual_cost: 0,
      status: "open",
      visibility_scope: ["supervisor", "boss"],
      source_event_id: e.id
    }));
}
function inferTitle(e) {
  if (/concrete|コンクリ/i.test(e.note)) return "コンクリート搬入遅延への対応を決める";
  if (/material|資材|材料/i.test(e.note)) return "資材不足への代替手段を決める";
  if (/approval|承認/i.test(e.note)) return "承認待ち案件の処理方針を決める";
  return `${e.event_type} に対する対応方針を決める`;
}
function inferDelay(e) { const m = e.note.match(/(\d+)\s*(?:日|days?)/i); return m ? Number(m[1]) : /遅|delay|pending/i.test(e.note) ? 3 : 1; }
function inferCost(e) { const m = e.note.match(/(?:¥|￥|cost\s*=)\s*([\d,]+)/i); return m ? Number(m[1].replace(/,/g, "")) : 50000; }
function inferDownstream(e) { return /major|critical|主要|全体|工程/i.test(e.note) ? 8 : /資材|concrete|コンクリ/i.test(e.note) ? 6 : 3; }
function inferDepth(e) { return /major|critical|主要|全体/i.test(e.note) ? 4 : 2; }
function inferUncertainty(e) { return /未定|不明|確認中|unknown|maybe/i.test(e.note) ? 75 : 35; }

function axisScores(d) {
  return {
    time: clamp(35 + d.delay_days * 7),
    money: clamp(d.impact_cost / 10000 * 10),
    safety: clamp(d.blocked_state === "blocked" && /危険|safety/i.test(d.constraint_reason) ? 90 : 20),
    legal: clamp(/契約|法|permit|許可|legal/i.test(d.constraint_reason) ? 80 : 25),
    human: clamp(25 + d.downstream_block_count * 6),
    client: clamp(/顧客|施主|customer|client/i.test(d.constraint_reason) ? 85 : 30)
  };
}

export function scoreDecisionDebt(d, weights = DEFAULT_WEIGHTS) {
  const breakdown = axisScores(d);
  const weighted = Object.entries(breakdown).reduce((sum, [k, v]) => sum + v * (weights[k] ?? 0), 0);
  const delayFactor = 1 + Math.min(d.delay_days, 30) / 50;
  const downstreamFactor = 1 + Math.min(d.downstream_block_count, 20) / 20;
  const dependencyFactor = 1 + Math.min(d.dependency_depth, 6) / 10;
  const uncertaintyFactor = 1 + clamp(d.uncertainty_score) / 200;
  const total = clamp(weighted * delayFactor * downstreamFactor * dependencyFactor * uncertaintyFactor);
  const counterfactualCost = Math.round(d.impact_cost * delayFactor * downstreamFactor);
  return { ...d, pressure_total: Number(total.toFixed(2)), breakdown, counterfactual_cost: counterfactualCost, reason: `${d.delay_days}日停滞・下流${d.downstream_block_count}件・依存深度${d.dependency_depth}段を考慮すると、先に処理する優先度が高い。` };
}

export function rankDecisionDebts(debts, weights = DEFAULT_WEIGHTS) {
  return debts.map((d) => scoreDecisionDebt(d, weights)).sort((a, b) => (b.pressure_total - a.pressure_total) || (b.downstream_block_count - a.downstream_block_count) || a.id.localeCompare(b.id)).map((d, i) => ({ ...d, rank: i + 1 }));
}

export function simulate30Days(debts, weights = DEFAULT_WEIGHTS) {
  const ranked = rankDecisionDebts(debts, weights);
  const scenarios = [["A", "全放置", () => ranked], ["B", "Top 1処理", () => ranked.slice(1)], ["C", "Top 3処理", () => ranked.slice(3)], ["D", "ランダム処理", () => ranked.filter((_, i) => i % 3 !== 0)]];
  return scenarios.map(([key, label, pick]) => { const remaining = pick(); return { key, label, unresolved_count_30d: remaining.length, explosion_events: remaining.filter((d) => d.pressure_total >= 70).length, impact_cost: remaining.reduce((s, d) => s + d.counterfactual_cost, 0), downstream_block_count: remaining.reduce((s, d) => s + d.downstream_block_count, 0) }; });
}

export function processEvents(events, weights = DEFAULT_WEIGHTS) {
  const normalized = events.map((e, i) => normalizeEvent(e, i));
  const candidates = extractDecisionCandidates(normalized);
  const ranked = rankDecisionDebts(candidates, weights);
  return { events: normalized, decisionDebts: ranked, simulation: simulate30Days(ranked, weights) };
}

export function csvToEvents(csv) {
  const lines = String(csv).trim().split(/\r?\n/).filter(Boolean);
  if (lines.length < 2) return [];
  const headers = lines.shift().split(",").map((x) => x.trim());
  return lines.map((line, i) => { const parts = line.split(","); const obj = Object.fromEntries(headers.map((h, j) => [h, parts[j]?.trim() ?? ""])); return normalizeEvent({ ...obj, id: obj.id || `CSV-${i + 1}` }, i); });
}
