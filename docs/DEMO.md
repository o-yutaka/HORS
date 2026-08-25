# 5分デモ

## 起動

```bash
npm install
npm run seed
npm run dev
```

ブラウザで `http://localhost:3100` を開く。

## 見せる順序

1. TODAY'S DECISION で「今日やるべき1つ」を最初に見せる。
2. Pressure 6軸、Delay、Downstream、Dependency を開く。
3. Decision Debt一覧でTop 10を見る。
4. 30-DAY COUNTERFACTUALで「放置 / Top1 / Top3 / ランダム」を比較する。
5. `POST /api/import-csv` に1行追加し、順位が変わることを見せる。

## 営業メッセージ

> 記録は今のまま。今日決めるべきことだけ出します。

既存の施工管理SaaSを置き換えず、CSV / Excel / LINE / 現場イベントから未決判断をDecision Debtとして整理する。

## 商談で確認する数字

- 未決判断件数
- 平均未決日数
- Top Pressure
- 下流ブロック数
- 30日シミュレーションの爆発イベント数
- 実際に処理された判断数
