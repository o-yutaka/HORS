# 現場データOS

**Decision Debt Intelligence Service for construction and field operations.**

> 記録は今のまま。今日決めるべきことだけ出す。

## 北極星

既存の施工管理SaaS、Excel、CSV、LINE、写真、PDFなどを置き換えず、現場の現実を

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

へ変換し、監督・責任者が「今日どの判断を先に処理すべきか」を理解できるサービスにする。

## Product

**現場の未決判断をDecision Debtとして定量化し、放置による下流影響を可視化して、今日処理すべき判断を順位付けするDecision Intelligenceサービス。**

「AI施工管理」「写真整理」「工程管理」「議事録AI」「DXコンサル」を主商品にしない。

## Commercial-first

最初は巨大なSaaSではなく、以下の順で販売する。

1. Decision Debt 現場診断
2. 有料Pilot
3. 月額運用サービス
4. 反復処理だけSaaS化

顧客に既存システムの置換を要求しない。

## v1 Core

- Decision Debt
- Pressure Engine
- Dependency Graph
- Priority Ranking
- 30日Counterfactual Simulation
- Execution Evidence

Coreの判定は決定論的ロジックを正とし、LLMは候補抽出・要約などの補助層に限定する。

## Primary ICP

- 従業員2〜30人程度
- 建設・設備・内装・電気・管工事など
- 複数現場を同時運営
- LINE / Excel / PDF / 写真が混在
- 既存SaaSは導入済みでも判断が追いつかない

## Current Stage

**Prototype → Demo → Diagnostic → Paid Pilot** のCommercial-first開発。

## Repository

`service/` がサービス本体、`docs/` が仕様・販売実証資料、`PROGRESS.md` と `SERVICE_STATUS.md` が継続実行の正本。

## Important

GitHub上のリポジトリ表示名が旧来の `HORS` のままの場合でも、プロジェクト内部の正式名称は **現場データOS** とする。
