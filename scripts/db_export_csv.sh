#!/bin/bash

# データベースCSVエクスポートスクリプト
# 使用方法: ./db_export_csv.sh [fixed|selection|all]

echo "📊 PostgreSQL CSVエクスポート"
echo "============================"
echo ""

# 引数チェック
EXPORT_TYPE=${1:-"all"}
if [ "$EXPORT_TYPE" != "fixed" ] && [ "$EXPORT_TYPE" != "selection" ] && [ "$EXPORT_TYPE" != "all" ]; then
    echo "使用方法: $0 [fixed|selection|all]"
    echo "  fixed     : 固定銘柄分析データ"
    echo "  selection : 銘柄選定分析データ"
    echo "  all       : 全データ（デフォルト）"
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

# エクスポートディレクトリの作成
EXPORT_DIR="./csv_exports"
mkdir -p $EXPORT_DIR

# タイムスタンプ
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 固定銘柄分析データのエクスポート
if [ "$EXPORT_TYPE" = "fixed" ] || [ "$EXPORT_TYPE" = "all" ]; then
    echo "📈 固定銘柄分析データをCSVエクスポート中..."
    
    FIXED_CSV="$EXPORT_DIR/fixed_stock_analysis_$TIMESTAMP.csv"
    
    docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
    COPY (
        SELECT 
            f.id,
            f.execution_date,
            COALESCE(a.model_name || ' (' || a.provider || ')', f.model_id) as model_name,
            f.stock_code,
            f.buy_date,
            f.buy_price,
            f.sell_date,
            f.sell_price,
            f.predicted_price,
            f.profit_loss,
            f.return_rate,
            f.prediction_accuracy,
            f.period_days,
            f.notes,
            f.created_at
        FROM fixed_stock_analysis f
        LEFT JOIN ai_models a ON f.model_id = a.model_code
        ORDER BY f.created_at DESC
    ) TO STDOUT WITH CSV HEADER ENCODING 'UTF8'
    " > $FIXED_CSV
    
    echo "✅ 固定銘柄分析CSV完了: $FIXED_CSV"
fi

# 銘柄選定分析データのエクスポート
if [ "$EXPORT_TYPE" = "selection" ] || [ "$EXPORT_TYPE" = "all" ]; then
    echo "🎯 銘柄選定分析データをCSVエクスポート中..."
    
    SELECTION_CSV="$EXPORT_DIR/stock_selection_analysis_$TIMESTAMP.csv"
    
    docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
    COPY (
        SELECT 
            s.id,
            s.execution_date,
            s.analysis_period,
            COALESCE(a.model_name || ' (' || a.provider || ')', s.model_id) as model_name,
            s.stock_code,
            s.selection_reason,
            s.buy_date,
            s.buy_price,
            s.sell_date,
            s.sell_price,
            s.profit_loss,
            s.return_rate,
            s.period_days,
            s.notes,
            s.created_at
        FROM stock_selection_analysis s
        LEFT JOIN ai_models a ON s.model_id = a.model_code
        ORDER BY s.created_at DESC
    ) TO STDOUT WITH CSV HEADER ENCODING 'UTF8'
    " > $SELECTION_CSV
    
    echo "✅ 銘柄選定分析CSV完了: $SELECTION_CSV"
fi

# 統合レポートの作成
if [ "$EXPORT_TYPE" = "all" ]; then
    echo "📋 統合レポートを作成中..."
    
    REPORT_CSV="$EXPORT_DIR/analysis_summary_$TIMESTAMP.csv"
    
    docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
    COPY (
        SELECT 
            'fixed_stock' as analysis_type,
            COALESCE(a.model_name || ' (' || a.provider || ')', f.model_id) as model_name,
            f.stock_code,
            f.execution_date,
            f.buy_price,
            f.sell_price,
            f.profit_loss,
            f.return_rate,
            f.prediction_accuracy,
            NULL as analysis_period,
            NULL as selection_reason,
            f.period_days,
            f.created_at
        FROM fixed_stock_analysis f
        LEFT JOIN ai_models a ON f.model_id = a.model_code
        UNION ALL
        SELECT 
            'stock_selection' as analysis_type,
            COALESCE(a.model_name || ' (' || a.provider || ')', s.model_id) as model_name,
            s.stock_code,
            s.execution_date,
            s.buy_price,
            s.sell_price,
            s.profit_loss,
            s.return_rate,
            NULL as prediction_accuracy,
            s.analysis_period,
            s.selection_reason,
            s.period_days,
            s.created_at
        FROM stock_selection_analysis s
        LEFT JOIN ai_models a ON s.model_id = a.model_code
        ORDER BY created_at DESC
    ) TO STDOUT WITH CSV HEADER ENCODING 'UTF8'
    " > $REPORT_CSV
    
    echo "✅ 統合レポートCSV完了: $REPORT_CSV"
fi

echo ""
echo "📄 エクスポートファイル一覧:"
echo "----------------------------"
ls -lh $EXPORT_DIR/*$TIMESTAMP*

echo ""
echo "📊 データ統計:"
echo "-------------"

if [ "$EXPORT_TYPE" = "fixed" ] || [ "$EXPORT_TYPE" = "all" ]; then
    FIXED_LINES=$(wc -l < $FIXED_CSV)
    echo "固定銘柄分析: $((FIXED_LINES - 1)) レコード"
fi

if [ "$EXPORT_TYPE" = "selection" ] || [ "$EXPORT_TYPE" = "all" ]; then
    SELECTION_LINES=$(wc -l < $SELECTION_CSV)
    echo "銘柄選定分析: $((SELECTION_LINES - 1)) レコード"
fi

echo ""
echo "💡 分析のヒント:"
echo "---------------"
echo "• Excel/Google Sheetsでピボットテーブル作成"
echo "• Python/Rでの統計分析"
echo "• Power BIやTableauでの可視化"
echo "• 勝率・平均リターンの月次トレンド分析"
