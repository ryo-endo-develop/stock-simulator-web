#!/bin/bash

# データベースダンプスクリプト
# 使用方法: ./db_dump.sh [full|data-only]

echo "💾 PostgreSQL データベースダンプ"
echo "==============================="
echo ""

# 引数チェック
DUMP_TYPE=${1:-"full"}
if [ "$DUMP_TYPE" != "full" ] && [ "$DUMP_TYPE" != "data-only" ]; then
    echo "使用方法: $0 [full|data-only]"
    echo "  full      : スキーマ + データの完全ダンプ（デフォルト）"
    echo "  data-only : データのみダンプ"
    exit 1
fi

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

# ダンプディレクトリの作成
DUMP_DIR="./database_dumps"
mkdir -p $DUMP_DIR

# タイムスタンプ
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

if [ "$DUMP_TYPE" = "full" ]; then
    echo "🗃️  完全ダンプ（スキーマ + データ）を作成中..."
    DUMP_FILE="$DUMP_DIR/stock_simulator_full_$TIMESTAMP.sql"
    
    docker exec $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME > $DUMP_FILE
    
    echo "✅ 完全ダンプ完了: $DUMP_FILE"
    
elif [ "$DUMP_TYPE" = "data-only" ]; then
    echo "📊 データのみダンプを作成中..."
    DUMP_FILE="$DUMP_DIR/stock_simulator_data_$TIMESTAMP.sql"
    
    docker exec $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME --data-only > $DUMP_FILE
    
    echo "✅ データダンプ完了: $DUMP_FILE"
fi

# ファイル情報表示
echo ""
echo "📄 ダンプファイル情報:"
echo "--------------------"
ls -lh $DUMP_FILE
echo ""

# ダンプ内容のサマリー
echo "📊 ダンプ内容サマリー:"
echo "--------------------"
if [ "$DUMP_TYPE" = "full" ]; then
    grep -c "CREATE TABLE" $DUMP_FILE | xargs -I {} echo "テーブル数: {}"
fi

grep -c "INSERT INTO" $DUMP_FILE | xargs -I {} echo "INSERT文数: {}"

echo ""
echo "🔧 復元コマンド:"
echo "---------------"
echo "docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < $DUMP_FILE"

echo ""
echo "💡 追加のエクスポートオプション:"
echo "-------------------------------"
echo "CSVエクスポート（固定銘柄分析）:"
echo "  ./db_export_csv.sh fixed"
echo ""
echo "CSVエクスポート（銘柄選定分析）:"
echo "  ./db_export_csv.sh selection"
echo ""
echo "CSVエクスポート（全データ）:"
echo "  ./db_export_csv.sh all"
