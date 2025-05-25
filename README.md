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

# 2. 動作確認
open http://localhost:8000
```

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
