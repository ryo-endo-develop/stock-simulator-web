#!/bin/bash

# データベーステーブル確認スクリプト
# 使用方法: ./db_check.sh

echo "🔍 PostgreSQL データベース確認ツール"
echo "====================================="
echo ""

# Dockerコンテナが起動しているか確認
if ! docker compose ps | grep -q "postgres.*Up"; then
    echo "❌ PostgreSQLコンテナが起動していません"
    echo "   以下のコマンドで起動してください:"
    echo "   docker compose up -d"
    exit 1
fi

echo "✅ PostgreSQLコンテナが起動中です"
echo ""

# データベース接続情報
DB_CONTAINER="stock_simulator_web-db-1"
DB_NAME="stock_simulator"
DB_USER="user"
DB_PASSWORD="password"

echo "📊 データベース情報:"
echo "   ホスト: localhost:5432"
echo "   データベース: $DB_NAME"
echo "   ユーザー: $DB_USER"
echo ""

echo "📋 利用可能なテーブル一覧:"
echo "----------------------------"
docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
\dt
"

echo ""
echo "📊 各テーブルのレコード数:"
echo "-------------------------"

# AIモデルテーブル
AI_MODELS_COUNT=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM ai_models;")
echo "🤖 ai_models: $AI_MODELS_COUNT 件"

# 固定銘柄分析テーブル
FIXED_COUNT=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM fixed_stock_analysis;")
echo "📈 fixed_stock_analysis: $FIXED_COUNT 件"

# 銘柄選定分析テーブル
SELECTION_COUNT=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM stock_selection_analysis;")
echo "🎯 stock_selection_analysis: $SELECTION_COUNT 件"

echo ""
echo "🔧 詳細確認コマンド:"
echo "--------------------"
echo "全データ確認:"
echo "  ./db_show_all.sh"
echo ""
echo "特定テーブル確認:"
echo "  docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c \"SELECT * FROM ai_models;\""
echo "  docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c \"SELECT * FROM fixed_stock_analysis ORDER BY created_at DESC LIMIT 10;\""
echo "  docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c \"SELECT * FROM stock_selection_analysis ORDER BY created_at DESC LIMIT 10;\""
echo ""
echo "SQLシェル接続:"
echo "  docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME"
