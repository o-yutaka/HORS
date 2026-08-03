import type { CompetitionArtifact, CompetitionProfile, IntelligenceRecord, IntelligenceReport } from "./contracts.js";

function normalize(text: string): string {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function claimsFrom(artifact: CompetitionArtifact): IntelligenceRecord[] {
  return artifact.body.split(/\r?\n|(?<=[.!?])\s+/).map((claim) => claim.trim()).filter((claim) => claim.length >= 24).slice(0, 50).map((claim) => ({
    artifactId: artifact.id,
    claim,
    evidence: [artifact.sourceUrl ?? artifact.id],
    confidence: artifact.kind === "rule" || artifact.kind === "metric" ? 1 : artifact.kind === "paper" ? 0.85 : 0.65,
    tags: [artifact.kind],
  }));
}

export class IntelligenceLayer {
  synthesize(profile: CompetitionProfile, artifacts: readonly CompetitionArtifact[]): IntelligenceReport {
    const records = artifacts.flatMap(claimsFrom);
    const groups = new Map<string, IntelligenceRecord[]>();
    for (const record of records) {
      const key = normalize(record.claim).replace(/\b(not|no|never|without)\b/g, "").trim();
      groups.set(key, [...(groups.get(key) ?? []), record]);
    }
    const contradictions = [...groups.entries()].flatMap(([claim, items]) => {
      const polarity = new Set(items.map((item) => /\b(not|no|never|without)\b/i.test(item.claim)));
      return polarity.size > 1 ? [{ claim, artifactIds: items.map((item) => item.artifactId) }] : [];
    });
    return {
      profile,
      records,
      contradictions,
      provenance: artifacts.map((artifact) => ({ artifactId: artifact.id, ...(artifact.sourceUrl ? { sourceUrl: artifact.sourceUrl } : {}) })),
    };
  }
}
