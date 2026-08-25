import { DEFAULT_WEIGHTS, HIGH_PRESSURE_THRESHOLD, SIMULATION_DAYS } from "./core.js";

export function buildDiagnosticReport(state, meta = {}) {
  const top = state.decisionDebts[0];
  const totalPressure = Number(state.decisionDebts.reduce((sum, d) => sum + d.pressure_total, 0).toFixed(2));
  const totalEstimatedCost = state.decisionDebts.reduce((sum, d) => sum + d.estimated_counterfactual_cost, 0);
  const baseline = state.simulation.find((x) => x.key === "A");
  const top1 = state.simulation.find((x) => x.key === "B");
  const top3 = state.simulation.find((x) => x.key === "C");
  return {
    report_type: "decision_debt_diagnostic",
    generated_at: new Date().toISOString(),
    engine: {
      name: "Decision Debt Engine",
      version: "decision-debt-v1.1",
      high_pressure_threshold: HIGH_PRESSURE_THRESHOLD,
      simulation_days: SIMULATION_DAYS,
      weights: DEFAULT_WEIGHTS
    },
    site: meta.site ?? "demo-site",
    customer: meta.customer ?? "demo-customer",
    summary: {
      decision_debt_count: state.decisionDebts.length,
      total_pressure: totalPressure,
      high_pressure_count: state.decisionDebts.filter((d) => d.pressure_total >= HIGH_PRESSURE_THRESHOLD).length,
      average_delay_days: state.decisionDebts.length
        ? Number((state.decisionDebts.reduce((s, d) => s + d.delay_days, 0) / state.decisionDebts.length).toFixed(1))
        : 0,
      estimated_counterfactual_cost_total: totalEstimatedCost,
      top_pressure: top?.pressure_total ?? 0,
      top_decision: top?.title ?? null,
      downstream_block_count: top?.downstream_block_count ?? 0
    },
    today_decision: top ? {
      rank: top.rank,
      title: top.title,
      pressure_total: top.pressure_total,
      breakdown: top.breakdown,
      reason: top.reason,
      estimated_counterfactual_cost: top.estimated_counterfactual_cost
    } : null,
    decision_debt_top10: state.decisionDebts.slice(0, 10).map(d => ({
      rank: d.rank,
      title: d.title,
      delay_days: d.delay_days,
      pressure_total: d.pressure_total,
      downstream_block_count: d.downstream_block_count,
      dependency_depth: d.dependency_depth,
      estimated_counterfactual_cost: d.estimated_counterfactual_cost
    })),
    counterfactual_effect: {
      assumption: "処理したDecision Debtは初日から負債残高から除外し、残存案件のみ時間経過させる決定論的シナリオ。",
      all_vs_top1: baseline && top1 ? {
        high_pressure_avoided_at_30d: baseline.final_high_pressure_count - top1.final_high_pressure_count,
        estimated_cost_reduction: baseline.estimated_counterfactual_cost_30d - top1.estimated_counterfactual_cost_30d
      } : null,
      all_vs_top3: baseline && top3 ? {
        high_pressure_avoided_at_30d: baseline.final_high_pressure_count - top3.final_high_pressure_count,
        estimated_cost_reduction: baseline.estimated_counterfactual_cost_30d - top3.estimated_counterfactual_cost_30d
      } : null
    },
    simulation: state.simulation,
    evidence: {
      source: "deterministic-engine",
      core_scoring: "deterministic",
      llm_used_for_core_scoring: false,
      value_status: "computed_estimate",
      customer_observed_metrics: null,
      note: "Pressure・下流負荷・反実仮想コストは入力データと決定論的ルールから算出した診断推定値。顧客実績ではない。実績値はExecution Evidenceとして別途記録する。"
    }
  };
}
