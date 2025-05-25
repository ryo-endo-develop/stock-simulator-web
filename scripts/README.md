# 🛠️ データベース管理スクリプト

このディレクトリには、PostgreSQL データベースの操作・管理用スクリプトが含まれています。

## 📋 スクリプト一覧

| スクリプト         | 説明                 | 使用方法                                     |
| ------------------ | -------------------- | -------------------------------------------- |
| `db_check.sh`      | データベース状況確認 | `./db_check.sh`                              |
| `db_show_all.sh`   | 全データ表示         | `./db_show_all.sh`                           |
| `db_reset.sh`      | データベースリセット | `./db_reset.sh`                              |
| `db_dump.sh`       | データベースダンプ   | `./db_dump.sh [full\|data-only]`             |
| `db_restore.sh`    | データベース復元     | `./db_restore.sh <dump_file>`                |
| `db_export_csv.sh` | CSV エクスポート     | `./db_export_csv.sh [fixed\|selection\|all]` |

## 🚀 クイックスタート

### 1. スクリプトに実行権限を付与

```bash
chmod +x scripts/*.sh
```

### 2. 基本的な操作フロー

```bash
# データベース状況確認
./scripts/db_check.sh

# 全データの表示
./scripts/db_show_all.sh

# CSVエクスポート
./scripts/db_export_csv.sh all

# データベースのダンプ
./scripts/db_dump.sh full
```

## 📊 各スクリプトの詳細

### 🔍 データベース確認 (`db_check.sh`)

```bash
./scripts/db_check.sh
```

**機能:**

- PostgreSQL コンテナの起動状況確認
- テーブル一覧の表示
- 各テーブルのレコード数表示
- 詳細確認コマンドの案内

**出力例:**

```
🔍 PostgreSQL データベース確認ツール
=====================================

✅ PostgreSQLコンテナが起動中です

📋 利用可能なテーブル一覧:
----------------------------
 Schema |           Name            | Type  | Owner
--------+---------------------------+-------+-------
 public | ai_models                 | table | user
 public | fixed_stock_analysis      | table | user
 public | stock_selection_analysis  | table | user

📊 各テーブルのレコード数:
-------------------------
🤖 ai_models: 16 件
📈 fixed_stock_analysis: 5 件
🎯 stock_selection_analysis: 3 件
```

### 📊 全データ表示 (`db_show_all.sh`)

```bash
./scripts/db_show_all.sh
```

**機能:**

- AI モデル一覧の表示
- 固定銘柄分析の最新 10 件表示
- 銘柄選定分析の最新 10 件表示
- 統計サマリーの表示

### 🗑️ データベースリセット (`db_reset.sh`)

```bash
./scripts/db_reset.sh
```

**機能:**

- 分析データの完全削除
- AI モデルデータの再投入
- 確認プロンプト付きで安全に実行

**注意事項:**

- **全ての分析データが削除されます**
- 実行前に必要に応じてダンプを取得してください

### 💾 データベースダンプ (`db_dump.sh`)

```bash
# 完全ダンプ（スキーマ + データ）
./scripts/db_dump.sh full

# データのみダンプ
./scripts/db_dump.sh data-only
```

**機能:**

- PostgreSQL 標準の pg_dump を使用
- タイムスタンプ付きファイル名で自動保存
- `database_dumps/` ディレクトリに保存

**出力ファイル例:**

- `database_dumps/stock_simulator_full_20250525_120000.sql`
- `database_dumps/stock_simulator_data_20250525_120000.sql`

### 🔄 データベース復元 (`db_restore.sh`)

```bash
./scripts/db_restore.sh ./database_dumps/stock_simulator_full_20250525_120000.sql
```

**機能:**

- ダンプファイルからデータベースを復元
- 復元前後のレコード数比較
- 確認プロンプト付きで安全に実行

### 📈 CSV エクスポート (`db_export_csv.sh`)

```bash
# 固定銘柄分析データのみ
./scripts/db_export_csv.sh fixed

# 銘柄選定分析データのみ
./scripts/db_export_csv.sh selection

# 全データ + 統合レポート
./scripts/db_export_csv.sh all
```

**機能:**

- PostgreSQL の COPY コマンドを使用
- UTF-8 エンコーディングで Excel 対応
- AI モデル名を人間が読みやすい形式で出力
- `csv_exports/` ディレクトリに保存

**出力ファイル例:**

- `csv_exports/fixed_stock_analysis_20250525_120000.csv`
- `csv_exports/stock_selection_analysis_20250525_120000.csv`
- `csv_exports/analysis_summary_20250525_120000.csv`

## 🔧 高度な使用方法

### データベース直接接続

```bash
# SQLシェルに接続
docker exec -it stock_simulator_web-db-1 psql -U user -d stock_simulator

# 特定のクエリを実行
docker exec stock_simulator_web-db-1 psql -U user -d stock_simulator -c "
SELECT model_id, COUNT(*), AVG(return_rate)
FROM fixed_stock_analysis
GROUP BY model_id
ORDER BY AVG(return_rate) DESC;
"
```

### バックアップの自動化

```bash
# 毎日午前2時にダンプを取得（crontabの例）
0 2 * * * cd /path/to/stock_simulator_web && ./scripts/db_dump.sh full

# 週次でCSVエクスポート（毎週日曜日午前3時）
0 3 * * 0 cd /path/to/stock_simulator_web && ./scripts/db_export_csv.sh all
```

### データ移行

```bash
# 開発環境から本番環境へのデータ移行
# 1. 開発環境でダンプ取得
./scripts/db_dump.sh full

# 2. ダンプファイルを本番環境にコピー
scp database_dumps/stock_simulator_full_20250525_120000.sql production-server:/path/to/dumps/

# 3. 本番環境で復元
./scripts/db_restore.sh /path/to/dumps/stock_simulator_full_20250525_120000.sql
```

## 📁 ディレクトリ構成

```
scripts/
├── 📄 README.md              # このファイル
├── 🔍 db_check.sh            # データベース状況確認
├── 📊 db_show_all.sh         # 全データ表示
├── 🗑️  db_reset.sh           # データベースリセット
├── 💾 db_dump.sh             # データベースダンプ
├── 🔄 db_restore.sh          # データベース復元
├── 📈 db_export_csv.sh       # CSVエクスポート
├── 📁 database_dumps/        # ダンプファイル保存先
└── 📁 csv_exports/           # CSVファイル保存先
```

## ⚠️ 注意事項

### セキュリティ

- **本番環境では適切なアクセス制御を設定してください**
- ダンプファイルには機密データが含まれる可能性があります
- CSV ファイルの取り扱いに注意してください

### パフォーマンス

- 大量データのダンプ・復元には時間がかかります
- 本番環境での実行時は業務時間外を推奨します
- 定期的な VACUUM・ANALYZE 実行を検討してください

### データ整合性

- 復元前には必ず現在のデータをバックアップしてください
- 異なるスキーマバージョン間での復元は注意が必要です

## 🆘 トラブルシューティング

### よくある問題と解決方法

**Q: "PostgreSQL コンテナが起動していません" エラーが出る**

```bash
# Docker Composeでコンテナを起動
docker compose up -d

# コンテナ状況確認
docker compose ps
```

**Q: "permission denied" エラーが出る**

```bash
# スクリプトに実行権限を付与
chmod +x scripts/*.sh
```

**Q: 復元時に "relation does not exist" エラーが出る**

```bash
# 完全ダンプ（スキーマ含む）を使用してください
./scripts/db_dump.sh full
./scripts/db_restore.sh database_dumps/stock_simulator_full_*.sql
```

**Q: CSV ファイルが文字化けする**

- UTF-8 BOM 付きでエクスポートされています
- Excel で CSV を開く際は「テキストファイルウィザード」を使用してください

---

**Happy Database Management! 🗄️💪**
