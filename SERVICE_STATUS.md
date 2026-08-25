# SERVICE STATUS

## Current Stage
Prototype → Demo

## Product
現場データOS — Decision Debt Intelligence

## Current ICP
専門工事・小規模建設会社（2〜30人程度、多現場、判断待ちが発生する企業）

## Current Offer
Decision Debt現場診断

## Demo Status
完成（repository implementation complete; local execution pending networked environment verification）

## Pilot Status
未実施

## Core Status
- Deterministic Decision Debt Engine: 実装済み
- Pressure Engine v2: 実装済み
- External pressure weights: 実装済み
- Priority Ranking: 実装済み
- 30-day Counterfactual Simulation: 実装済み
- CSV import: 実装済み
- Supervisor one-screen UI: 実装済み
- Role-aware API scope: v1実装済み
- Diagnostic report JSON: 実装済み
- Core acceptance tests: 実装済み

## Latest Customer Evidence
- Decision Debt: 未取得
- Top Pressure: 未取得
- Downstream Block: 未取得
- Before/After: 未取得

## Commercial Hypothesis
- Price: 診断 19,800円〜 / Pilot 49,800〜99,800円 / 月額 29,800〜79,800円（仮説）
- Objection: 既存SaaSとの重複、データ提供の手間、効果の説明
- Reason to Buy: 「記録は今のまま。今日決めるべきことだけ出す。」

## Next Action
1. ネットワーク接続可能な開発環境で npm test / npm run seed / npm run dev を実行
2. 5分デモでランタイム問題を潰す
3. 初回現場データを受領
4. 有料Pilotへ接続

## Unresolved Decisions
- GitHubのrepository display nameを `genba-data-os` に変更するプラットフォーム操作
- 最初の実データ提供企業
- 顧客ヒアリングによる価格更新

## Evidence Rule
実測していないBefore/Afterや売上・削減時間は記録しない。

## North Star Deviation
なし
