#!/bin/bash

# データベース全データ表示スクリプト
# 使用方法: ./db_show_all.sh

echo "📊 PostgreSQL 全データ表示"
echo "=========================="
echo ""

# データベース接続情報
DB_CONTAINER="stock_simulator_web-db-1"
DB_NAME="stock_simulator"
DB_USER="user"

# Dockerコンテナ確認
if ! docker compose ps | grep -q "postgres.*Up"; then
    echo "❌ PostgreSQLコンテナが起動していません"
    exit 1
fi

echo "🤖 AIモデル一覧:"
echo "----------------"
docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT 
    id,
    model_code,
    model_name,
    provider,
    model_type,
    is_active,
    created_at::date
FROM ai_models 
ORDER BY provider, model_name;
"

echo ""
echo "📈 固定銘柄分析（最新10件）:"
echo "----------------------------"
docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT 
    id,
    execution_date::date,
    model_id,
    stock_code,
    buy_price,
    sell_price,
    predicted_price,
    profit_loss,
    return_rate,
    prediction_accuracy,
    period_days,
    created_at::date
FROM fixed_stock_analysis 
ORDER BY created_at DESC 
LIMIT 10;
"

echo ""
echo "🎯 銘柄選定分析（最新10件）:"
echo "----------------------------"
docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT 
    id,
    execution_date::date,
    analysis_period,
    model_id,
    stock_code,
    buy_price,
    sell_price,
    profit_loss,
    return_rate,
    period_days,
    created_at::date
FROM stock_selection_analysis 
ORDER BY created_at DESC 
LIMIT 10;
"

echo ""
echo "📊 統計サマリー:"
echo "---------------"
docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT 
    'fixed_stock_analysis' as table_name,
    COUNT(*) as total_records,
    AVG(return_rate) as avg_return_rate,
    AVG(prediction_accuracy) as avg_prediction_accuracy,
    COUNT(CASE WHEN return_rate > 0 THEN 1 END)::float / COUNT(*) * 100 as win_rate_percent
FROM fixed_stock_analysis
UNION ALL
SELECT 
    'stock_selection_analysis' as table_name,
    COUNT(*) as total_records,
    AVG(return_rate) as avg_return_rate,
    NULL as avg_prediction_accuracy,
    COUNT(CASE WHEN return_rate > 0 THEN 1 END)::float / COUNT(*) * 100 as win_rate_percent
FROM stock_selection_analysis;
"
