import type { CompetitionArtifact, CompetitionProfile, CompetitionRisk, CompetitionSource, CompetitionKind } from "./contracts.js";

const METRICS = ["rmse", "mae", "mse", "log loss", "logloss", "auc", "accuracy", "f1", "map@", "ndcg", "bleu", "dice", "iou"];

function corpus(artifacts: readonly CompetitionArtifact[]): string {
  return artifacts.map((item) => `${item.title}\n${item.body}`).join("\n").toLowerCase();
}

function inferKind(text: string): CompetitionKind {
  if (/image|pixel|segmentation|object detection/.test(text)) return "vision";
  if (/time series|timestamp|forecast|temporal/.test(text)) return "timeseries";
  if (/simulation|agent|game|environment/.test(text)) return "simulation";
  if (/source code|program|compiler|repository/.test(text)) return "code";
  if (/text|language|token|sentence|document/.test(text)) return "nlp";
  if (/csv|table|column|feature/.test(text)) return "tabular";
  return "unknown";
}

function detectMetric(text: string): string | null {
  return METRICS.find((metric) => text.includes(metric)) ?? null;
}

function risks(text: string, artifacts: readonly CompetitionArtifact[]): CompetitionRisk[] {
  const found: CompetitionRisk[] = [];
  if (/leak|future information|target encoded/.test(text)) found.push({ code: "leakage", severity: "high", evidence: ["Potential leakage language detected"], mitigation: "Use split-aware feature generation and an explicit leakage audit." });
  if (!detectMetric(text)) found.push({ code: "metric_mismatch", severity: "high", evidence: ["No supported evaluation metric detected"], mitigation: "Resolve the official metric before model selection or CV design." });
  if (!artifacts.some((item) => item.kind === "submission")) found.push({ code: "submission_contract", severity: "medium", evidence: ["Submission artifact is absent"], mitigation: "Collect sample_submission and validate columns, row order, types, and missing values." });
  if (!artifacts.some((item) => item.kind === "rule")) found.push({ code: "rule_constraint", severity: "critical", evidence: ["Official rules are absent"], mitigation: "Block execution until official rules and external-data constraints are collected." });
  return found;
}

export class CompetitionAnalyzer {
  analyze(source: CompetitionSource, title: string, artifacts: readonly CompetitionArtifact[], declaredKind?: CompetitionKind): CompetitionProfile {
    const text = corpus(artifacts);
    const metric = detectMetric(text);
    const submission = artifacts.find((item) => item.kind === "submission");
    const columns = Array.isArray(submission?.metadata?.columns) ? submission.metadata.columns.filter((value): value is string => typeof value === "string") : [];
    const constraints = artifacts.filter((item) => item.kind === "rule").flatMap((item) => item.body.split(/\r?\n/).map((line) => line.trim()).filter(Boolean));
    const objective = metric && /rmse|mae|mse|log loss|logloss/.test(metric) ? "minimize" : metric ? "maximize" : "unknown";
    return { source, title, kind: declaredKind ?? inferKind(text), metric, objective, submissionColumns: columns, constraints, risks: risks(text, artifacts), artifactCount: artifacts.length };
  }
}
