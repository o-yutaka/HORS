# 現場データOS サービス販売実行指示書 v3.0

## 目的

施工管理SaaSをもう1個作るのではなく、既存のANDPAD / KANNA / Excel / CSV / LINE / 写真 / PDFなどを置き換えず、現場の現実を以下へ変換する。

```text
Reality
→ Decision Candidate
→ Decision Debt
→ Pressure
→ Priority
→ Counterfactual Simulation
→ Action
→ Evidence
```

北極星は次の4つ。

1. 現場1社分のデータを流し込める
2. 未決判断が生む停滞・圧力・下流影響を可視化する
3. 監督/責任者が「今日やるべき1つ」を根拠付きで判断できる
4. 顧客が金を払う理由を1画面で理解できる

## 商品定義

**現場の未決判断をDecision Debtとして定量化し、放置による下流影響を可視化して、今日処理すべき判断を順位付けするDecision Intelligenceサービス。**

AI施工管理、写真整理、工程管理、議事録AI、DXコンサルを主商品にしない。

## 商材

### 商品A: Decision Debt 現場診断

CSV / Excel / PDF / LINEログ / 写真metadata等を受領し、データ取込 → イベント整理 → 判断候補抽出 → Decision Debt化 → Pressure計算 → Top 10 → 30日Simulation → 改善レポートまで実施する。

### 商品B: 有料Pilot

1社・1〜3現場に限定して実データで継続利用。Decision Debt件数、平均未決日数、Pressure、下流ブロック、爆発イベント、処理された判断数、確認時間を測定する。

### 商品C: 月額運用

顧客がデータを送り続けることで、毎週または毎月Decision Debtレポートを返す。

### 商品D: 将来SaaS

有料顧客で繰り返し使われた処理だけをSaaS化する。

## ICP

最初は従業員2〜30人程度の建設・設備・内装・電気・管工事等。複数現場を持ち、LINE / Excel / PDF / 写真が混在し、既存SaaSを導入していても判断が追いついていない企業を優先する。

## 中心ループ

```text
External Reality
→ Event Normalization
→ Decision Candidate Extraction
→ Decision Debt Engine
→ Pressure Engine
→ Dependency Graph
→ Priority Ranking
→ Counterfactual Simulation
→ Recommended Next Action
→ Execution Evidence
→ Reality
```

LLMをコア判定器にしない。Decision Debt / Pressure / Ranking / Simulationは決定論的Python/TypeScriptロジックを正とする。

## Decision Debt

最低限保持する項目：

```text
id
site_id
title
owner_role
decision_state
blocked_state
constraint_reason
delay_days
impact_cost
downstream_block_count
dependency_depth
first_blocked_at
last_state_change_at
uncertainty_score
counterfactual_cost
status
visibility_scope
```

Task = やる仕事。Decision = 決める必要があること。Decision Debt = 未決のまま時間経過することで増える影響。

## Pressure Engine

6軸：time / money / safety / legal / human / client。

重みは `config/pressure_weights.json` に外出しする。

```text
weighted_pressure
× delay_factor
× downstream_factor
× dependency_factor
× uncertainty_factor
```

同じ入力から同じ結果。乱数禁止。seed再現可能。tie-break固定。計算根拠をAPIで返す。

## Counterfactual Simulation

必須シナリオ：

- A: 全Decision Debtを放置
- B: Top 1のみ処理
- C: Top 3を処理
- D: ランダム処理

最低限出力：30日後未決件数、爆発イベント数、推定impact_cost、downstream block数、高圧力案件数。

## UI v1

Supervisor 1画面のみ。

1. TODAY'S DECISION
2. WHY #1
3. DECISION DEBT
4. REALITY TIMELINE
5. SIMULATION
6. DATA INGEST

冒頭1秒以内に「今日何を決めるべきか」が分かること。タブを増やさない。

## RoleRouter

roles: `tanto / supervisor / keiri / boss`

APIはフロントで隠すのではなく、認可前にSELECT範囲を限定する。visibility_scopeのカンマ区切り方式は禁止し、`entity_visibility(entity_type, entity_id, role)` を使用する。

v1 UIはSupervisorのみ。開発用role resolverは利用可能だが、`?role=` を本番認証として扱わない。

## 入力

v1コネクタはCSV / LINE mock / photo metadata。

CSV例：`date,site,event_type,status,note`

LINE mock例：`[監督] 明日コンクリ遅れる`

photoはmetadataのみ。画像解析はv1では行わない。

## 販売メッセージ

> 記録は今のシステムのまま。今日決めるべきことだけ出す。

> 未決判断が何日残っていて、何件の仕事を塞いでいて、放置するとどこまで広がるかを見える化します。

> 既存の施工管理システムを捨てる必要はありません。

## 仮説価格

Decision Debt診断: 19,800円〜

有料Pilot: 49,800〜99,800円程度

月額運用: 29,800〜79,800円程度

価格は顧客ヒアリングで更新する。v1に決済機能を作らない。

## 販売導線

直接営業 → 無料/低価格診断 → 有料Pilot → 月額運用 → 紹介。

## 禁止事項

ANDPAD/KANNA等の施工管理機能を再実装しない。写真管理SaaSを作らない。工程管理SaaSを作らない。AI議事録を主商品にしない。巨大管理画面を作らない。マルチテナント・決済・複雑な認証をv1で作らない。AIエージェントをコア判定にしない。LLMでPressure順位を決めない。

## Phase

0 骨格
1 core
2 backend + RoleRouter
3 seed + simulator
4 Supervisor UI
5 connectors
6 Decision Intelligence
7 Demo package
8 Pilot package
9 Service operation

## 受け入れ基準

- `git clone → npm install → npm run dev` で起動
- seed後Decision Debt 10件以上
- TODAY'S DECISION表示
- 6軸内訳 / delay / downstream / dependency表示
- 「なぜ1位か」決定論的表示
- CSV importで変化
- 30日Simulation再現可能
- Top1処理後に再計算
- role scopeテストあり
- supervisorにbillingなし
- keiriには許可されたbilling summaryあり
- READMEに起動・seed・role説明
- tests green
- 5分デモ成立
- 架空顧客デモ成立
- 1現場診断レポート生成可能

## Commercial Ready

技術完成だけでは完了としない。架空現場5分デモ、実データ1現場診断、Top1根拠説明、顧客による1判断処理、Before/After取得、有料Pilot価格提示、再現可能な納品、顧客データ安全運用手順が揃って初めてサービス販売可能とする。

## 継続実行

作業開始時に `/PROGRESS.md`、`/SERVICE_STATUS.md`、本指示書を読む。古い競合情報を鵜呑みにしない。セッション終了時に `/PROGRESS.md` と `/SERVICE_STATUS.md` を更新する。
