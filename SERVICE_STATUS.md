# SERVICE STATUS

## Current Stage
Prototype / Demo / Diagnostic → Paid Pilot preparation

## Product
現場データOS — Decision Debt Accounting

## Current ICP
専門工事・小規模建設会社（2〜30人程度、多現場、判断待ちが発生する企業）

## Current Offer
Decision Debt現場診断

## Demo Status
実装済み。seedデータで5分デモ可能な状態。

## Pilot Status
未実施。Commercial validation issue #2 を起票済み。

## Latest Customer Evidence
- Decision Debt: 未取得（実顧客）
- Top Pressure: 未取得（実顧客）
- Downstream Block: 未取得（実顧客）
- Before/After: 未取得（実顧客）

## Commercial Hypothesis
- Diagnostic: ¥19,800+
- Pilot: ¥49,800〜99,800
- Monthly operation: ¥29,800〜79,800
- Reason to Buy: 「記録は今のまま。未決判断を負債として計測し、今日決めるべき1つだけ出す。」

## Product Evidence
- Deterministic Decision Debt engine: implemented
- Pressure Engine v2: implemented
- Dependency/downstream scoring: implemented（現状はheuristic v1; graph expansion is later）
- Real daily 30-day counterfactual simulation: implemented
- Robust CSV ingest with validation: implemented
- Supervisor UI: implemented
- Role-aware API with dev-role header scopes: implemented
- Diagnostic report with engine/version/config provenance: implemented
- Counterfactual value deltas for Top1/Top3: implemented
- Commercial value metrics: defined
- Competitive positioning: documented
- CI verification workflow: configured

## Competitive Finding
主要競合は施工管理、現場データ基盤、建設向けAI、会議からの未決抽出、経営ダッシュボードまで進化している。したがって「AI判断」や「未決可視化」だけでは差別化にならない。現場データOSは既存システムを置換せず、未決判断の残高・Pressure・下流負荷・放置vs処理の反実仮想を一体で扱うDecision Debt Accountingという狭いカテゴリを狙う。競合比較は公開情報からのカテゴリ整理であり、非搭載機能の不存在を断定しない。

## Evidence Rule
- Computed estimates ≠ customer-observed outcomes
- Monetary/counterfactual values are estimates until validated against customer evidence
- Customer Before/After remains blank until real pilot data exists

## Next Action
Run local `npm run verify` and the 5-minute demo, then acquire the first real field dataset and sell the first Decision Debt diagnostic.

## Open Commercial Gate
Issue #2 — first paid Decision Debt diagnostic.

## North Star Deviation
なし
