# LLM 投資アイデア検証ツール (Web 版)

PostgreSQL と FastAPI を使用した Web アプリケーション

## 機能

- **固定銘柄分析**: 特定銘柄に対する LLM の予測精度を検証
- **銘柄選定分析**: LLM の銘柄選定能力を期間別に検証
- **履歴分析**: 過去の分析結果の統計的評価

## ローカル開発環境 (Docker)

### 1. リポジトリをクローン

```bash
git clone <repository-url>
cd stock_simulator_web
```

### 2. Docker Compose で起動

```bash
docker-compose up --build
```

### 3. アクセス

- アプリケーション: http://localhost:8000
- PostgreSQL: localhost:5432

## API 仕様

### エンドポイント

- `GET /` - ホームページ
- `GET /fixed-stock` - 固定銘柄分析フォーム
- `POST /fixed-stock` - 固定銘柄分析実行
- `POST /fixed-stock/save` - 結果保存
- `GET /stock-selection` - 銘柄選定分析フォーム
- `POST /stock-selection` - 銘柄選定分析実行
- `POST /stock-selection/save` - 結果保存
- `GET /history` - 履歴分析

## データベーススキーマ

### fixed_stock_analysis テーブル

- id (主キー)
- execution_date (実行日)
- model_id (LLM モデル名)
- stock_code (銘柄コード)
- buy_date, buy_price (購入日・価格)
- sell_date, sell_price (売却日・価格)
- predicted_price (予測価格)
- profit_loss (損益)
- return_rate (騰落率)
- prediction_accuracy (予測精度)
- period_days (期間)
- notes (備考)
- created_at (作成日時)

### stock_selection_analysis テーブル

- id (主キー)
- execution_date (実行日)
- analysis_period (分析期間)
- model_id (LLM モデル名)
- stock_code (銘柄コード)
- selection_reason (選定理由)
- buy_date, buy_price (購入日・価格)
- sell_date, sell_price (売却日・価格)
- profit_loss (損益)
- return_rate (騰落率)
- period_days (期間)
- notes (備考)
- created_at (作成日時)

## 技術スタック

- **Backend**: FastAPI + SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: Jinja2 + Bootstrap 5
- **株価データ**: yfinance
- **Deploy**: Render

## 注意事項

- 検証目的のツールであり、実際の投資判断には使用しないでください
- 株価データは yfinance から取得するため、インターネット接続が必要です
- 実際の取引手数料や税金は考慮されていません
