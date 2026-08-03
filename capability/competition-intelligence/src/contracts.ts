export type CompetitionKind = "tabular" | "vision" | "nlp" | "timeseries" | "simulation" | "code" | "unknown";

export interface CompetitionSource {
  readonly platform: string;
  readonly slug: string;
  readonly url?: string;
}

export interface CompetitionArtifact {
  readonly id: string;
  readonly kind: "rule" | "dataset" | "metric" | "submission" | "discussion" | "notebook" | "code" | "paper";
  readonly title: string;
  readonly body: string;
  readonly sourceUrl?: string;
  readonly author?: string;
  readonly publishedAt?: string;
  readonly metadata?: Readonly<Record<string, unknown>>;
}

export interface CompetitionAdapter {
  identify(source: CompetitionSource): Promise<{ title: string; kind?: CompetitionKind }>;
  collect(source: CompetitionSource): Promise<readonly CompetitionArtifact[]>;
}

export interface CompetitionRisk {
  readonly code: "leakage" | "metric_mismatch" | "submission_contract" | "rule_constraint" | "distribution_shift" | "insufficient_evidence";
  readonly severity: "low" | "medium" | "high" | "critical";
  readonly evidence: readonly string[];
  readonly mitigation: string;
}

export interface CompetitionProfile {
  readonly source: CompetitionSource;
  readonly title: string;
  readonly kind: CompetitionKind;
  readonly metric: string | null;
  readonly objective: "minimize" | "maximize" | "unknown";
  readonly submissionColumns: readonly string[];
  readonly constraints: readonly string[];
  readonly risks: readonly CompetitionRisk[];
  readonly artifactCount: number;
}

export interface IntelligenceRecord {
  readonly artifactId: string;
  readonly claim: string;
  readonly evidence: readonly string[];
  readonly confidence: number;
  readonly tags: readonly string[];
}

export interface IntelligenceReport {
  readonly profile: CompetitionProfile;
  readonly records: readonly IntelligenceRecord[];
  readonly contradictions: readonly { claim: string; artifactIds: readonly string[] }[];
  readonly provenance: readonly { artifactId: string; sourceUrl?: string }[];
}
