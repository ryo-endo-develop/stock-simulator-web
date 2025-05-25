#!/bin/bash

# データベース復元スクリプト
# 使用方法: ./db_restore.sh <dump_file>

echo "🔄 PostgreSQL データベース復元"
echo "============================="
echo ""

# 引数チェック
if [ $# -eq 0 ]; then
    echo "使用方法: $0 <dump_file>"
    echo ""
    echo "利用可能なダンプファイル:"
    echo "------------------------"
    if [ -d "./database_dumps" ]; then
        ls -la ./database_dumps/*.sql 2>/dev/null || echo "  ダンプファイルが見つかりません"
    else
        echo "  database_dumpsディレクトリが見つかりません"
    fi
    echo ""
    echo "例:"
    echo "  $0 ./database_dumps/stock_simulator_full_20250525_120000.sql"
    exit 1
fi

DUMP_FILE="$1"

# ダンプファイルの存在確認
if [ ! -f "$DUMP_FILE" ]; then
    echo "❌ ダンプファイルが見つかりません: $DUMP_FILE"
    exit 1
fi

echo "📄 復元対象ファイル: $DUMP_FILE"
echo "📊 ファイルサイズ: $(ls -lh "$DUMP_FILE" | awk '{print $5}')"

# データベース接続情報
DB_CONTAINER="stock_simulator_web-db-1"
DB_NAME="stock_simulator"
DB_USER="user"

# Dockerコンテナ確認
if ! docker compose ps | grep -q "postgres.*Up"; then
    echo "❌ PostgreSQLコンテナが起動していません"
    echo "   docker compose up -d で起動してください"
    exit 1
fi

echo ""
echo "⚠️  注意: 既存のデータは上書きされます"
echo ""

# 確認プロンプト
read -p "データベースを復元しますか？ (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ 復元をキャンセルしました"
    exit 0
fi

echo ""
echo "📊 復元前のデータベース状況:"
echo "----------------------------"

# 復元前のレコード数を確認
FIXED_COUNT_BEFORE=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM fixed_stock_analysis;" 2>/dev/null || echo "0")
SELECTION_COUNT_BEFORE=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM stock_selection_analysis;" 2>/dev/null || echo "0")

echo "固定銘柄分析: $FIXED_COUNT_BEFORE 件"
echo "銘柄選定分析: $SELECTION_COUNT_BEFORE 件"

echo ""
echo "🔄 データベース復元中..."

# データベースの復元実行
if docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < "$DUMP_FILE"; then
    echo "✅ データベース復元完了"
else
    echo "❌ データベース復元でエラーが発生しました"
    exit 1
fi

echo ""
echo "📊 復元後のデータベース状況:"
echo "----------------------------"

# 復元後のレコード数を確認
FIXED_COUNT_AFTER=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM fixed_stock_analysis;" 2>/dev/null || echo "0")
SELECTION_COUNT_AFTER=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM stock_selection_analysis;" 2>/dev/null || echo "0")

echo "固定銘柄分析: $FIXED_COUNT_AFTER 件"
echo "銘柄選定分析: $SELECTION_COUNT_AFTER 件"

echo ""
echo "📈 データ変更サマリー:"
echo "---------------------"
echo "固定銘柄分析: $FIXED_COUNT_BEFORE → $FIXED_COUNT_AFTER 件"
echo "銘柄選定分析: $SELECTION_COUNT_BEFORE → $SELECTION_COUNT_AFTER 件"

echo ""
echo "🎉 データベース復元完了！"
echo ""
echo "📝 次のステップ:"
echo "  1. アプリケーションを再起動: docker compose restart app"
echo "  2. ブラウザでアクセス: http://localhost:8000"
echo "  3. データが正常に復元されているか確認してください"
