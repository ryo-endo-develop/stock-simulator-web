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

| スクリプト         | 説明         | 使用例                           |
| ------------------ | ------------ | -------------------------------- |
| `db_check.sh`      | DB 状況確認  | `./scripts/db_check.sh`          |
| `db_show_all.sh`   | 全データ表示 | `./scripts/db_show_all.sh`       |
| `db_reset.sh`      | DB リセット  | `./scripts/db_reset.sh`          |
| `db_dump.sh`       | DB ダンプ    | `./scripts/db_dump.sh full`      |
| `db_restore.sh`    | DB 復元      | `./scripts/db_restore.sh <file>` |
| `db_export_csv.sh` | CSV 出力     | `./scripts/db_export_csv.sh all` |

**詳細**: `scripts/README.md`

## 📅 運用手順ガイド

### 🚀 初回セットアップ（最初に1回だけ）

```bash
# 1. プロジェクトを起動
docker-compose up -d

# 2. スクリプトに実行権限を付与
chmod +x setup_scripts.sh
./setup_scripts.sh

# 3. 動作確認
open http://localhost:8000
```

### 🔄 週次運用フロー（毎週繰り返し）

---

## 📋 **金曜日夕方：次週の準備**

### 🤖 **ステップ1: スクリプトでプロンプト生成**
```bash
./weekly_workflow.sh prepare
```
**実行されること：**
- 来週の日付を自動計算
- プロンプトファイル生成（例：`prompts/generated/weekly_prompt_20250525.md`）
- AI回答保存用フォルダ作成（例：`ai_responses/20250525/`）
- 回答テンプレートファイルの準備

### 👤 **ステップ2: 手動でAIに質問（土日に実行）**

**2-1. プロンプトファイルを開く**
```bash
# 生成されたプロンプトを確認
open prompts/generated/weekly_prompt_$(date +%Y%m%d).md
```

**2-2. Claude 3.5 Sonnetに質問**
1. https://claude.ai にアクセス
2. 上記プロンプトの**全文をコピー&ペースト**
3. 回答を取得
4. 回答を `ai_responses/20250525/claude_response.md` に**全文コピー&ペースト**

**2-3. ChatGPT-4に質問**
1. https://chatgpt.com にアクセス
2. 同じプロンプトの**全文をコピー&ペースト**
3. 回答を取得
4. 回答を `ai_responses/20250525/chatgpt_response.md` に**全文コピー&ペースト**

**2-4. Gemini Proに質問**
1. https://gemini.google.com にアクセス
2. 同じプロンプトの**全文をコピー&ペースト**
3. 回答を取得
4. 回答を `ai_responses/20250525/gemini_response.md` に**全文コピー&ペースト**

**⚠️ 重要：AI回答の保存形式**
```
ai_responses/20250525/
├── claude_response.md    ← Claudeの回答をそのまま全文保存
├── chatgpt_response.md   ← ChatGPTの回答をそのまま全文保存
└── gemini_response.md    ← Geminiの回答をそのまま全文保存
```

---

## 📊 **月曜日朝：予測をシステムに記録**

### 🤖 **ステップ3: スクリプトでアプリ起動確認**
```bash
./weekly_workflow.sh record
```
**実行されること：**
- アプリケーションの起動状況確認
- データベース接続確認
- 記録手順の案内表示

### 👤 **ステップ4: 手動でブラウザ操作（約15分）**

**4-1. アプリケーションにアクセス**
```
http://localhost:8000
```

**4-2. 銘柄選定分析を記録（各AI×5銘柄=15件）**

🔵 **Claude分析の記録（5件）**
1. `http://localhost:8000/stock-selection` にアクセス
2. `ai_responses/20250525/claude_response.md` を開いて回答を確認
3. 以下を入力：
   ```
   分析期間: 1週間
   LLMモデル: Claude 3.5 Sonnet
   銘柄コード: 4689  ← AIの1位銘柄
   選定理由: PayPayの海外展開加速、25日移動平均線上抜け...  ← AIの回答をコピー
   購入日: 2025-05-26  ← 来週月曜日
   備考: 期待リターン+5.2%  ← AIの期待リターン等
   ```
4. 「実行」ボタンをクリック
5. 結果確認後「保存」ボタンをクリック
6. **同じ手順を2位〜5位銘柄で繰り返し**

🟢 **ChatGPT分析の記録（5件）**
1. 同じ画面で続けて入力
2. `ai_responses/20250525/chatgpt_response.md` の回答を参照
3. LLMモデルを「ChatGPT-4」に変更
4. **1位〜5位銘柄を同様に記録**

🟡 **Gemini分析の記録（5件）**
1. 同じ画面で続けて入力
2. `ai_responses/20250525/gemini_response.md` の回答を参照
3. LLMモデルを「Gemini Pro」に変更
4. **1位〜5位銘柄を同様に記録**

**4-3. トヨタ株の固定銘柄分析を記録（各AI×1件=3件）**

1. `http://localhost:8000/fixed-stock` にアクセス
2. 各AIの回答からトヨタ予測を入力：
   ```
   LLMモデル: Claude 3.5 Sonnet
   銘柄コード: 7203
   予測価格: 3120  ← AIの週末終値予想
   購入日: 2025-05-26
   売却日: 2025-05-30
   備考: 中立シナリオ、3,050-3,150円レンジ想定
   ```
3. **同様にChatGPTとGeminiの予測も記録**

**📊 記録完了確認**
- 合計18件（銘柄選定15件 + 固定銘柄3件）が記録されているか確認
- `http://localhost:8000/history` で記録内容を確認

---

## 🔍 **金曜日夕方：結果の検証**

### 🤖 **ステップ5: スクリプトで結果分析**
```bash
./weekly_workflow.sh verify
```
**実行されること：**
- 週次実績の自動集計
- CSVファイルのエクスポート
- データベースのバックアップ
- 履歴分析ページへの案内

### 👤 **ステップ6: 手動で結果確認（約10分）**

**6-1. パフォーマンスランキング確認**
```
http://localhost:8000/history
```
- **モデル別勝率**をチェック
- **予測精度ランキング**を確認
- **今週の結果**を前週と比較

**6-2. 詳細分析（任意）**
- `csv_exports/` フォルダのCSVファイルをExcelで開く
- 月次トレンドや銘柄別パフォーマンスを分析
- 失敗した予測の要因を調査

**6-3. 改善点の検討**
- AIの回答品質に問題がないか確認
- プロンプトの改善点を検討
- 次週の運用計画を立てる

---

## 📋 **運用チェックリスト**

### ✅ **金曜日夕方（15分）**
- [ ] `./weekly_workflow.sh prepare` 実行
- [ ] プロンプトファイル生成確認
- [ ] AI回答保存フォルダ作成確認

### ✅ **土日（30分）**
- [ ] Claude 3.5 Sonnetに質問・回答保存
- [ ] ChatGPT-4に質問・回答保存
- [ ] Gemini Proに質問・回答保存
- [ ] 回答ファイルの保存確認

### ✅ **月曜日朝（15分）**
- [ ] `./weekly_workflow.sh record` 実行
- [ ] アプリケーション起動確認
- [ ] Claude銘柄5件 + トヨタ1件記録
- [ ] ChatGPT銘柄5件 + トヨタ1件記録
- [ ] Gemini銘柄5件 + トヨタ1件記録
- [ ] 合計18件の記録完了確認

### ✅ **金曜日夕方（10分）**
- [ ] `./weekly_workflow.sh verify` 実行
- [ ] パフォーマンスランキング確認
- [ ] 今週の勝率・精度確認
- [ ] CSVエクスポート完了確認
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

### **Q: AI回答の品質が悪い**
- 市場環境の補足情報をプロンプトに追加
- 過去の成功例を参考にプロンプト調整
- 質問する時間帯を変更（市場の開いている時間など）

---

## 💡 **運用成功のコツ**

1. **継続性が最重要**：毎週必ず実行する
2. **詳細記録**：AIの回答は省略せず全文保存
3. **複数比較**：最低3つのAIで比較分析
4. **改善マインド**：月次でプロセスを見直す
5. **データ活用**：蓄積データから傾向を分析

---

## 🎯 **目標設定例**

- **短期（1ヶ月）**：週次運用の安定化
- **中期（3ヶ月）**：最優秀AIモデルの特定
- **長期（6ヶ月）**：プロンプト最適化による精度向上
- **応用**：独自の投資戦略アルゴリズム開発

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
