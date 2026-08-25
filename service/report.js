export function buildDiagnosticReport(state, meta = {}) {
  const top = state.decisionDebts[0];
  return {
    report_type: "decision_debt_diagnostic",
    generated_at: new Date().toISOString(),
    site: meta.site ?? "demo-site",
    customer: meta.customer ?? "demo-customer",
    summary: {
      decision_debt_count: state.decisionDebts.length,
      average_delay_days: state.decisionDebts.length
        ? Number((state.decisionDebts.reduce((s, d) => s + d.delay_days, 0) / state.decisionDebts.length).toFixed(1))
        : 0,
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
      counterfactual_cost: top.counterfactual_cost
    } : null,
    decision_debt_top10: state.decisionDebts.slice(0, 10).map(d => ({
      rank: d.rank,
      title: d.title,
      delay_days: d.delay_days,
      pressure_total: d.pressure_total,
      downstream_block_count: d.downstream_block_count,
      dependency_depth: d.dependency_depth,
      counterfactual_cost: d.counterfactual_cost
    })),
    simulation: state.simulation,
    evidence: {
      source: "deterministic-engine",
      llm_used_for_core_scoring: false,
      note: "数値は入力データと決定論的ルールから計算。実績値ではなく診断時点の推定値。"
    }
  };
}
