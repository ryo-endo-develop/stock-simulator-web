# 📊 LLM 投資アイデア検証ツール (Web 版)

PostgreSQL と FastAPI を使用した Web アプリケーション

## 🚀 機能

### 📈 分析機能

- **固定銘柄分析**: 特定銘柄に対する LLM の予測精度を検証
- **銘柄選定分析**: LLM の銘柄選定能力を期間別に検証
- **履歴分析・統計**: 過去の分析結果の統計的評価とモデル比較

### 📊 強化された履歴分析

- **モデル別パフォーマンスランキング**: LLM モデルの予測精度を比較
- **高度なフィルタリング**: 日付・モデル・騰落率での絞り込み
- **CSV エクスポート**: 分析データの詳細出力
- **リアルタイム統計**: 勝率・平均リターン・予測精度の追跡

### 🤖 週次プロンプト生成

- **自動プロンプト生成**: 生成 AI への質問文を自動作成
- **上位 5 銘柄選定**: 1 週間の上昇期待銘柄の予測依頼
- **個別銘柄分析**: トヨタ株の詳細予測
- **バックテスト連携**: 予測結果を直接システムで検証

## 📝 使用方法

### 1️⃣ 基本的な分析フロー

1. **固定銘柄分析**: http://localhost:8000/fixed-stock

   - LLM モデルを選択
   - 銘柄コードと予測価格を入力
   - 購入日・売却日を指定
   - 結果を保存して精度を検証

2. **銘柄選定分析**: http://localhost:8000/stock-selection

   - 分析期間 1 週間〜1 年）を選択
   - LLM が選んだ銘柄と理由を入力
   - 購入日を指定して自動計算
   - 結果を保存して選定能力を評価

3. **履歴分析**: http://localhost:8000/history
   - モデル別パフォーマンスランキングを確認
   - フィルターで結果を絞り込み
   - CSV エクスポートで詳細分析

### 2️⃣ 週次プロンプトでの予測ワークフロー

```bash
# 1. プロンプトを生成
cd prompts/
python generate_weekly_prompt.py

# 2. 生成されたプロンプトを確認
open generated/weekly_prompt_$(date +%Y%m%d).md
```

3. **プロンプトを Claude/ChatGPT に貼り付け**
4. **回答をシミュレーターに入力**
5. **1 週間後に結果を検証**

### 3️⃣ データエクスポートと分析

- **基本エクスポート**: 履歴ページの CSV ボタン
- **高度なエクスポート**: フィルタ条件付き CSV 出力
- **Excel での詳細分析**: ピボットテーブルやグラフ作成

## 🐳 ローカル開発環境 (Docker)

### 1. リポジトリをクローン

```bash
git clone <repository-url>
cd stock_simulator_web
```

### 2. Docker Compose で起動

```bash
docker compose up --build
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
├── 📄 weekly_workflow.sh        # 週次運用支援スクリプト
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
├── 📁 scripts/                  # データベース管理スクリプト
│   ├── README.md                  # スクリプト詳細説明
│   ├── db_check.sh               # DB状況確認
│   ├── db_show_all.sh            # 全データ表示
│   ├── db_reset.sh               # DBリセット
│   ├── db_dump.sh                # DBダンプ
│   ├── db_restore.sh             # DB復元
│   ├── db_export_csv.sh          # CSVエクスポート
│   ├── database_dumps/           # ダンプファイル保存先
│   └── csv_exports/              # CSVファイル保存先
├── 📁 ai_responses/             # AI回答管理
│   ├── README.md                  # 回答管理ガイド
│   ├── response_template.md       # 回答保存テンプレート
│   ├── 20250525/                 # 日付別回答フォルダ
│   └── archive/                  # 月次アーカイブ
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

| スクリプト         | 説明                     | 使用例                                   |
| ------------------ | ------------------------ | ---------------------------------------- |
| `auto_import.py`   | 🤖 AI 回答自動解析・投入 | `python scripts/auto_import.py 20250525` |
| `auto_update.py`   | 📊 結果自動更新          | `python scripts/auto_update.py 20250525` |
| `db_check.sh`      | DB 状況確認              | `./scripts/db_check.sh`                  |
| `db_show_all.sh`   | 全データ表示             | `./scripts/db_show_all.sh`               |
| `db_reset.sh`      | DB リセット              | `./scripts/db_reset.sh`                  |
| `db_dump.sh`       | DB ダンプ                | `./scripts/db_dump.sh full`              |
| `db_restore.sh`    | DB 復元                  | `./scripts/db_restore.sh <file>`         |
| `db_export_csv.sh` | CSV 出力                 | `./scripts/db_export_csv.sh all`         |

**詳細**: `scripts/README.md`

## 📅 運用手順ガイド

### 🚀 初回セットアップ（最初に 1 回だけ）

```bash
# 1. プロジェクトを起動
docker compose up -d

# 2. スクリプトに実行権限を付与
chmod +x setup_scripts.sh
./setup_scripts.sh

# 3. 動作確認
open http://localhost:8000
```

### 🔄 週次運用フロー（毎週繰り返し）

---

## 📋 **金曜日夕方：次週の準備（2 分）**

### 🤖 **ステップ 1: プロンプト自動生成**

```bash
./weekly_workflow.sh prepare
```

**実行されること：**

- 来週の日付を自動計算
- プロンプトファイル生成（例：`prompts/generated/weekly_prompt_20250525.md`）
- AI 回答保存用フォルダ作成（例：`ai_responses/20250525/`）
- 回答テンプレートファイルの準備

---

## 👤 **土日：AI に質問・回答保存（15 分）**

**手動作業のみ - 以下を順番に実行：**

### **1. Claude 3.5 Sonnet に質問**

1. https://claude.ai にアクセス
2. `prompts/generated/weekly_prompt_YYYYMMDD.md` の**全文をコピー&ペースト**
3. 回答を取得
4. 回答を `ai_responses/20250525/claude_response.md` に**全文保存**

### **2. ChatGPT-4 に質問**

1. https://chatgpt.com にアクセス
2. 同じプロンプトを**全文コピー&ペースト**
3. 回答を `ai_responses/20250525/chatgpt_response.md` に**全文保存**

### **3. Gemini Pro に質問**

1. https://gemini.google.com にアクセス
2. 同じプロンプトを**全文コピー&ペースト**
3. 回答を `ai_responses/20250525/gemini_response.md` に**全文保存**

---

## 🤖 **月曜日朝：AI 回答を自動投入（1 分）**

### **ステップ 1: 自動解析・投入実行**

```bash
./weekly_workflow.sh record
```

**自動で実行されること：**

- AI 回答ファイル（3 種類）を自動解析
- 銘柄情報・選定理由・トヨタ予測を抽出
- データベースに自動投入（合計 18 件）
  - Claude: 銘柄 5 件 + トヨタ 1 件 = 6 件
  - ChatGPT: 銘柄 5 件 + トヨタ 1 件 = 6 件
  - Gemini: 銘柄 5 件 + トヨタ 1 件 = 6 件
- 結果をブラウザで確認可能

---

## 🔍 **金曜日夕方：結果自動更新・検証（2 分）**

### **ステップ 1: 結果自動更新・分析**

```bash
./weekly_workflow.sh verify
```

**自動で実行されること：**

- 先週投入したデータの株価を自動取得
- 損益・騰落率・予測精度を自動計算
- パフォーマンス統計を自動更新
- CSV エクスポート自動実行
- データベースバックアップ自動実行
- 履歴分析ページで結果確認

---

## 📋 **運用チェックリスト**

### ✅ **金曜日夕方（15 分）**

- [ ] `./weekly_workflow.sh prepare` 実行
- [ ] プロンプトファイル生成確認
- [ ] AI 回答保存フォルダ作成確認

### ✅ **土日（30 分）**

- [ ] Claude 3.5 Sonnet に質問・回答保存
- [ ] ChatGPT-4 に質問・回答保存
- [ ] Gemini Pro に質問・回答保存
- [ ] 回答ファイルの保存確認

### ✅ **月曜日朝（15 分）**

- [ ] `./weekly_workflow.sh record` 実行
- [ ] アプリケーション起動確認
- [ ] Claude 銘柄 5 件 + トヨタ 1 件記録
- [ ] ChatGPT 銘柄 5 件 + トヨタ 1 件記録
- [ ] Gemini 銘柄 5 件 + トヨタ 1 件記録
- [ ] 合計 18 件の記録完了確認

### ✅ **金曜日夕方（10 分）**

- [ ] `./weekly_workflow.sh verify` 実行
- [ ] パフォーマンスランキング確認
- [ ] 今週の勝率・精度確認
- [ ] CSV エクスポート完了確認
- [ ] 次週準備の計画

---

## 🔧 **よくあるトラブルと対処法**

### **Q: アプリケーションにアクセスできない**

```bash
# コンテナ状況確認
docker-compose ps

# 再起動
docker-compose restart

# 完全リセット（最後の手段）
docker-compose down
docker-compose up -d
```

### **Q: データが正しく保存されない**

```bash
# データベース状況確認
./scripts/db_check.sh

# ログ確認
docker-compose logs app
```

### **Q: プロンプト生成でエラーが出る**

```bash
# Python環境確認
python --version

# 手動でプロンプトファイルを編集
open prompts/weekly_stock_prediction.md
```

### **Q: AI 回答の品質が悪い**

- 市場環境の補足情報をプロンプトに追加
- 過去の成功例を参考にプロンプト調整
- 質問する時間帯を変更（市場の開いている時間など）

---

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
