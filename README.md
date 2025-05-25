# 📊 LLM 投資アイデア検証ツール (Web 版)

PostgreSQL と FastAPI を使用した Web アプリケーション

## 🚀 機能

### 📈 分析機能
- **固定銘柄分析**: 特定銘柄に対する LLM の予測精度を検証
- **銘柄選定分析**: LLM の銘柄選定能力を期間別に検証
- **履歴分析・統計**: 過去の分析結果の統計的評価とモデル比較

### 📊 強化された履歴分析
- **モデル別パフォーマンスランキング**: LLMモデルの予測精度を比較
- **高度なフィルタリング**: 日付・モデル・騰落率での絞り込み
- **CSVエクスポート**: 分析データの詳細出力
- **リアルタイム統計**: 勝率・平均リターン・予測精度の追跡

### 🤖 週次プロンプト生成
- **自動プロンプト生成**: 生成AIへの質問文を自動作成
- **上位5銘柄選定**: 1週間の上昇期待銘柄の予測依頼
- **個別銘柄分析**: トヨタ株の詳細予測
- **バックテスト連携**: 予測結果を直接システムで検証

## 📝 使用方法

### 1️⃣ 基本的な分析フロー

1. **固定銘柄分析**: http://localhost:8000/fixed-stock
   - LLMモデルを選択
   - 銘柄コードと予測価格を入力
   - 購入日・売却日を指定
   - 結果を保存して精度を検証

2. **銘柄選定分析**: http://localhost:8000/stock-selection
   - 分析期間1週間〜1年）を選択
   - LLMが選んだ銘柄と理由を入力
   - 購入日を指定して自動計算
   - 結果を保存して選定能力を評価

3. **履歴分析**: http://localhost:8000/history
   - モデル別パフォーマンスランキングを確認
   - フィルターで結果を絞り込み
   - CSVエクスポートで詳細分析

### 2️⃣ 週次プロンプトでの予測ワークフロー

```bash
# 1. プロンプトを生成
cd prompts/
python generate_weekly_prompt.py

# 2. 生成されたプロンプトを確認
open generated/weekly_prompt_$(date +%Y%m%d).md
```

3. **プロンプトをClaude/ChatGPTに貼り付け**
4. **回答をシミュレーターに入力**
5. **1週間後に結果を検証**

### 3️⃣ データエクスポートと分析

- **基本エクスポート**: 履歴ページのCSVボタン
- **高度なエクスポート**: フィルタ条件付きCSV出力
- **Excelでの詳細分析**: ピボットテーブルやグラフ作成

## 🐳 ローカル開発環境 (Docker)

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

## 📎 プロジェクト構成

```
stock_simulator_web/
├── 📄 main.py                    # FastAPIアプリケーション
├── 📄 database.py               # データベース管理
├── 📄 stock_analyzer.py          # 株価データ分析
├── 📄 analytics.py              # 統計分析モジュール
├── 📁 templates/                # HTMLテンプレート
│   ├── base.html
│   ├── index.html
│   ├── fixed_stock.html
│   ├── stock_selection.html
│   └── history.html
├── 📁 prompts/                  # 週次プロンプト生成ツール
│   ├── README.md                  # 使用方法説明
│   ├── weekly_stock_prediction.md # プロンプトテンプレート
│   ├── generate_weekly_prompt.py  # プロンプト生成スクリプト
│   ├── sample_response.md         # 回答例・使用例
│   └── generated/                 # 生成されたプロンプト
├── 📄 docker-compose.yml
├── 📄 Dockerfile
└── 📄 requirements.txt
```

## 🔧 データベース管理スクリプト

### 🚀 スクリプト初期化

```bash
# スクリプトに実行権限を付与
chmod +x setup_scripts.sh
./setup_scripts.sh
```

### 📊 基本操作

```bash
# データベース状況確認
./scripts/db_check.sh

# 全データ表示
./scripts/db_show_all.sh

# CSVエクスポート
./scripts/db_export_csv.sh all

# データベースダンプ
./scripts/db_dump.sh full

# データベースリセット
./scripts/db_reset.sh
```

### 📁 スクリプト一覧

| スクリプト | 説明 | 使用例 |
|-----------|------|---------|
| `db_check.sh` | DB状況確認 | `./scripts/db_check.sh` |
| `db_show_all.sh` | 全データ表示 | `./scripts/db_show_all.sh` |
| `db_reset.sh` | DBリセット | `./scripts/db_reset.sh` |
| `db_dump.sh` | DBダンプ | `./scripts/db_dump.sh full` |
| `db_restore.sh` | DB復元 | `./scripts/db_restore.sh <file>` |
| `db_export_csv.sh` | CSV出力 | `./scripts/db_export_csv.sh all` |

**詳細**: `scripts/README.md`

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
