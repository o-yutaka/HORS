import { describe, expect, it } from "vitest";
import { CompetitionIntelligencePipeline, type CompetitionAdapter, type CompetitionSource } from "../src/index.js";

const source: CompetitionSource = { platform: "kaggle", slug: "demo" };
const adapter: CompetitionAdapter = {
  async identify() { return { title: "Demo Forecast", kind: "timeseries" }; },
  async collect() {
    return [
      { id: "rules", kind: "rule", title: "Rules", body: "External data is allowed only when public." },
      { id: "metric", kind: "metric", title: "Evaluation", body: "Submissions are evaluated using RMSE." },
      { id: "submission", kind: "submission", title: "sample_submission.csv", body: "Required format", metadata: { columns: ["id", "target"] } },
      { id: "discussion", kind: "discussion", title: "CV", body: "Random folds leak future information. Time-based folds should be used." },
    ] as const;
  },
};

describe("CompetitionIntelligencePipeline", () => {
  it("produces a metric-aware, evidence-grounded report", async () => {
    const report = await new CompetitionIntelligencePipeline(adapter).run(source);
    expect(report.profile.metric).toBe("rmse");
    expect(report.profile.objective).toBe("minimize");
    expect(report.profile.submissionColumns).toEqual(["id", "target"]);
    expect(report.profile.risks.some((risk) => risk.code === "leakage")).toBe(true);
    expect(report.records.length).toBeGreaterThan(0);
    expect(report.provenance).toHaveLength(4);
  });
});
