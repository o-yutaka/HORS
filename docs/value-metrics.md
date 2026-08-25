# Decision Debt Value Metrics

## 顧客価値の主指標

### 1. Decision Debt Balance
現在の未決判断件数。

### 2. Debt at Risk
高Pressureかつ一定期間以上停滞しているDecision Debt件数。

### 3. Downstream Block Load
未決判断によって塞がっている下流イベント/作業件数の合計。

### 4. Counterfactual Cost
現在の判断を放置した場合に見込まれる累積impact_costの代理指標。

### 5. Today's Top 1
当日最優先で処理すべきDecision Debt。

## 営業デモで最初に出す順番

```text
Decision Debt残高: 12
High-pressure: 4
下流ブロック: 31件
放置想定コスト: ¥1,240,000

TODAY'S TOP 1
「外装材の承認方針を決める」
```

## 成果証明

Pilot開始時点と終了時点で同じ指標を保存する。

```text
Before
Debt Balance: 42
High-pressure: 13
Downstream Block: 77
Counterfactual Cost: ¥4.2M

After
Debt Balance: 23
High-pressure: 4
Downstream Block: 29
Counterfactual Cost: ¥1.1M
```

数字は実測値のみ使用し、架空値は営業資料では「sample」と明示する。

## Positioning

「AIが判断する」ではなく、
「未決判断の残高・放置圧力・下流負荷を計測し、今日のTop 1を出す」。

これがDecision Debt Accountingの最小説明単位。
