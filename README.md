# 📊 LLM 投資アイデア検証ツール - 運用ガイド

PostgreSQL と FastAPI を使用した LLM 予測精度検証 Web アプリケーション

## 🎯 このツールの目的

1. **固定銘柄分析**: 特定銘柄に対する LLM の予測精度を検証
2. **銘柄選定分析**: LLM の銘柄選定能力を期間別に検証
3. **統計分析**: 複数 LLM モデルのパフォーマンス比較

## 🚀 初回セットアップ（最初に 1 回だけ）

```bash
# 1. プロジェクト起動
git clone <repository-url>
cd stock_simulator_web
docker compose up -d

# 2. スクリプト初期化
chmod +x setup_scripts.sh
./setup_scripts.sh

# 3. 動作確認
open http://localhost:8000
```

---

## 📅 週次運用フロー（毎週繰り返し）

### 🔄 **金曜日夕方：次週準備（2 分）**

```bash
./weekly_workflow.sh prepare
```

**自動実行されること：**

- 📝 来週のプロンプト生成：`prompts/generated/weekly_prompt_YYYYMMDD.md`
- 📁 AI 回答保存フォルダ作成：`ai_responses/YYYYMMDD/`
- 📋 回答テンプレート配布

---

### 👤 **土日：AI 質問・回答保存（15 分）**

**⚠️ この作業は手動必須**

#### 1. Claude 3.5 Sonnet

```bash
# 1. https://claude.ai にアクセス
# 2. prompts/generated/weekly_prompt_YYYYMMDD.md の全文をコピー&ペースト
# 3. 回答を ai_responses/YYYYMMDD/claude_response.md に全文保存
```

#### 2. ChatGPT-4

```bash
# 1. https://chatgpt.com にアクセス
# 2. 同じプロンプトを全文コピー&ペースト
# 3. 回答を ai_responses/YYYYMMDD/chatgpt_response.md に全文保存
```

#### 3. Gemini Pro

```bash
# 1. https://gemini.google.com にアクセス
# 2. 同じプロンプトを全文コピー&ペースト
# 3. 回答を ai_responses/YYYYMMDD/gemini_response.md に全文保存
```

---

### 📊 **月曜日朝：予測をシステム記録（15 分）**

```bash
./weekly_workflow.sh record
```

**自動実行：**

- アプリケーション起動確認
- データベース状況確認

**手動作業：ブラウザで以下を入力**

#### A. 銘柄選定分析（15 件）

**URL**: http://localhost:8000/stock-selection

**Claude 分析（5 件）**：

```
分析期間: 1週間
LLMモデル: Claude 3.5 Sonnet
銘柄コード: [AIの1位銘柄]
選定理由: [AIの選定理由をコピー]
購入日: [来週月曜日]
→ 実行・保存を5回繰り返し
```

**ChatGPT 分析（5 件）**：

- LLM モデルを「ChatGPT-4」に変更
- 同様に 5 銘柄を入力

**Gemini 分析（5 件）**：

- LLM モデルを「Gemini Pro」に変更
- 同様に 5 銘柄を入力

#### B. 固定銘柄分析（3 件）

**URL**: http://localhost:8000/fixed-stock

```
LLMモデル: Claude 3.5 Sonnet
銘柄コード: 7203
予測価格: [Claudeの週末終値予想]
購入日: [来週月曜日]
売却日: [来週金曜日]
→ 実行・保存

# ChatGPT-4、Gemini Proでも同様に実行
```

#### C. 記録完了確認

http://localhost:8000/history で合計 18 件が記録されているか確認

---

### 🔍 **金曜日夕方：結果検証（10 分）**

```bash
./weekly_workflow.sh verify
```

**自動実行：**

- 週次統計集計
- CSV エクスポート実行
- データベースバックアップ

**手動確認：**

1. **http://localhost:8000/history** でパフォーマンスランキング確認
2. 今週の勝率・予測精度をチェック
3. CSV ファイルで詳細分析（任意）

---

## 📋 運用チェックリスト

### ✅ 金曜日夕方（2 分）

- [ ] `./weekly_workflow.sh prepare` 実行
- [ ] プロンプトファイル生成確認
- [ ] AI 回答フォルダ作成確認

### ✅ 土日（15 分）

- [ ] Claude 回答保存完了
- [ ] ChatGPT 回答保存完了
- [ ] Gemini 回答保存完了
- [ ] 3 ファイルすべて保存確認

### ✅ 月曜日朝（15 分）

- [ ] `./weekly_workflow.sh record` 実行
- [ ] アプリケーション起動確認
- [ ] 銘柄選定分析 15 件入力完了
- [ ] 固定銘柄分析 3 件入力完了
- [ ] 履歴ページで 18 件確認

### ✅ 金曜日夕方（10 分）

- [ ] `./weekly_workflow.sh verify` 実行
- [ ] パフォーマンスランキング確認
- [ ] 勝率・精度データ確認
- [ ] 次週準備完了

---

## 🛠️ データベース管理

### 基本操作

```bash
# DB状況確認
./scripts/db_check.sh

# 全データ表示
./scripts/db_show_all.sh

# CSVエクスポート
./scripts/db_export_csv.sh all

# DBバックアップ
./scripts/db_dump.sh full

# DBリセット（注意）
./scripts/db_reset.sh
```

### スクリプト一覧

| スクリプト         | 説明         | 使用例                           |
| ------------------ | ------------ | -------------------------------- |
| `db_check.sh`      | DB 状況確認  | `./scripts/db_check.sh`          |
| `db_show_all.sh`   | 全データ表示 | `./scripts/db_show_all.sh`       |
| `db_reset.sh`      | DB リセット  | `./scripts/db_reset.sh`          |
| `db_dump.sh`       | DB ダンプ    | `./scripts/db_dump.sh full`      |
| `db_restore.sh`    | DB 復元      | `./scripts/db_restore.sh <file>` |
| `db_export_csv.sh` | CSV 出力     | `./scripts/db_export_csv.sh all` |

---

## 🔧 トラブルシューティング

### Q: アプリケーションにアクセスできない

```bash
# コンテナ確認
docker compose ps

# 再起動
docker compose restart

# 完全リセット
docker compose down && docker compose up -d
```

### Q: データが保存されない

```bash
# DB状況確認
./scripts/db_check.sh

# ログ確認
docker compose logs app
```

### Q: プロンプト生成エラー

```bash
# Python環境確認
python --version

# 手動編集
open prompts/weekly_stock_prediction.md
```

---

## 📊 技術仕様

### アクセス URL

- **アプリケーション**: http://localhost:8000
- **固定銘柄分析**: http://localhost:8000/fixed-stock
- **銘柄選定分析**: http://localhost:8000/stock-selection
- **履歴分析**: http://localhost:8000/history

### 技術スタック

- **Backend**: FastAPI + SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: Jinja2 + Bootstrap 5
- **株価データ**: yfinance

### ファイル構成

```
stock_simulator_web/
├── 📄 main.py                    # FastAPIアプリ
├── 📄 database.py               # DB管理
├── 📄 stock_analyzer.py         # 株価分析
├── 📄 analytics.py              # 統計分析
├── 📄 weekly_workflow.sh        # 週次運用スクリプト
├── 📁 templates/                # HTMLテンプレート
├── 📁 prompts/                  # プロンプト生成ツール
├── 📁 scripts/                  # DB管理スクリプト
├── 📁 ai_responses/             # AI回答管理
├── 📄 docker-compose.yml
├── 📄 Dockerfile
└── 📄 requirements.txt
```

---

## ⚠️ 重要な注意事項

1. **投資助言ではありません**: あくまで検証・研究目的のツールです
2. **手数料考慮なし**: 実際の取引手数料や税金は含まれていません
3. **データ取得**: yfinance を使用するためインターネット接続が必要
4. **営業日調整**: 休場日は直後の営業日データを使用
5. **バックアップ推奨**: 重要なデータは定期的にバックアップしてください

---

**Happy Trading Analysis! 📈🤖**
