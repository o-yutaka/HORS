export * from "./contracts.js";
export * from "./analyzer.js";
export * from "./intelligence.js";

import { CompetitionAnalyzer } from "./analyzer.js";
import { IntelligenceLayer } from "./intelligence.js";
import type { CompetitionAdapter, CompetitionSource, IntelligenceReport } from "./contracts.js";

export class CompetitionIntelligencePipeline {
  constructor(
    private readonly adapter: CompetitionAdapter,
    private readonly analyzer = new CompetitionAnalyzer(),
    private readonly intelligence = new IntelligenceLayer(),
  ) {}

  async run(source: CompetitionSource): Promise<IntelligenceReport> {
    const [identity, artifacts] = await Promise.all([
      this.adapter.identify(source),
      this.adapter.collect(source),
    ]);
    const profile = this.analyzer.analyze(source, identity.title, artifacts, identity.kind);
    return this.intelligence.synthesize(profile, artifacts);
  }
}
