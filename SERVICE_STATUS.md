# SERVICE STATUS

## Current Stage
Prototype / Demo / Diagnostic → Paid Pilot preparation

## Product
現場データOS — Decision Debt Intelligence / Decision Debt Accounting

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
- Dependency/downstream scoring: implemented
- 30-day counterfactual: implemented
- CSV ingest: implemented
- Supervisor UI: implemented
- Role-aware API: implemented
- Diagnostic report: implemented
- Commercial value metrics: defined
- Competitive positioning: documented
- CI test/typecheck workflow: configured

## Competitive Finding
主要競合は施工管理、現場データ基盤、AIによる個別業務支援、会議からの未決抽出、経営ダッシュボードまで進化している。一方、現場データOSはそれらを置換せず、未決判断の残高・Pressure・下流負荷・Counterfactualを一体で計測する狭いカテゴリを狙う。

## Next Action
Run local verification, then acquire the first real field dataset and sell the first Decision Debt diagnostic.

## Open Commercial Gate
Issue #2 — first paid Decision Debt diagnostic.

## North Star Deviation
なし
