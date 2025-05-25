# LLM投資アイデア検証ツール (Web版)

PostgreSQLとFastAPIを使用したWebアプリケーション

## 機能

- **固定銘柄分析**: 特定銘柄に対するLLMの予測精度を検証
- **銘柄選定分析**: LLMの銘柄選定能力を期間別に検証  
- **履歴分析**: 過去の分析結果の統計的評価

## ローカル開発環境 (Docker)

### 1. リポジトリをクローン
```bash
git clone <repository-url>
cd stock_simulator_web
```

### 2. Docker Composeで起動
```bash
docker-compose up --build
```

### 3. アクセス
- アプリケーション: http://localhost:8000
- PostgreSQL: localhost:5432

## Renderデプロイ

### 1. 環境変数設定
Renderのダッシュボードで以下の環境変数を設定:

```
DATABASE_URL=postgresql://user:password@host:port/database
```

### 2. ビルド設定
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `bash start.sh`

### 3. PostgreSQLデータベース
RenderのPostgreSQLサービスを作成し、DATABASE_URLを設定

## API仕様

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
- model_id (LLMモデル名)
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
- model_id (LLMモデル名)
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
- 株価データはyfinanceから取得するため、インターネット接続が必要です
- 実際の取引手数料や税金は考慮されていません
