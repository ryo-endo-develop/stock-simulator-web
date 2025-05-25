#!/bin/bash

# マイグレーション実行スクリプト
# 使用方法: ./scripts/run_migrations.sh

echo "🔄 データベースマイグレーション実行"
echo "================================="
echo ""

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

echo "✅ PostgreSQLコンテナが起動中です"
echo ""

# 既存データのバックアップを推奨
echo "📋 マイグレーション前の確認:"
echo "----------------------------"

# 現在のレコード数を表示
FIXED_COUNT=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM fixed_stock_analysis;" 2>/dev/null || echo "0")
SELECTION_COUNT=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM stock_selection_analysis;" 2>/dev/null || echo "0")

echo "固定銘柄分析: $FIXED_COUNT 件"
echo "銘柄選定分析: $SELECTION_COUNT 件"

echo ""
echo "⚠️  マイグレーションを実行します"
echo "   既存データは保持されますが、念のためバックアップを推奨します"
echo ""

# 確認プロンプト
read -p "続行しますか？ (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ マイグレーションをキャンセルしました"
    exit 0
fi

echo ""
echo "📦 バックアップ作成（推奨）:"
echo "./scripts/db_dump.sh full"
echo ""

# マイグレーション実行
echo "🔄 マイグレーション実行中..."
docker exec $DB_CONTAINER python3 -c "
import sys
sys.path.append('/app')
from migration_manager import MigrationManager

try:
    manager = MigrationManager()
    manager.run_pending_migrations()
    print('✅ マイグレーション完了')
except Exception as e:
    print(f'❌ マイグレーションエラー: {str(e)}')
    sys.exit(1)
"

echo ""
echo "📊 マイグレーション後の確認:"
echo "----------------------------"

# マイグレーション後のレコード数を表示
FIXED_COUNT_AFTER=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM fixed_stock_analysis;" 2>/dev/null || echo "0")
SELECTION_COUNT_AFTER=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM stock_selection_analysis;" 2>/dev/null || echo "0")

echo "固定銘柄分析: $FIXED_COUNT_AFTER 件 (変更: $((FIXED_COUNT_AFTER - FIXED_COUNT)))"
echo "銘柄選定分析: $SELECTION_COUNT_AFTER 件 (変更: $((SELECTION_COUNT_AFTER - SELECTION_COUNT)))"

# 新しいカラムの確認
echo ""
echo "📋 新しいカラムの確認:"
echo "--------------------"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'fixed_stock_analysis' 
AND column_name IN ('predicted_high', 'predicted_low', 'predicted_close', 'actual_high', 'actual_low', 'high_prediction_accuracy', 'low_prediction_accuracy', 'overall_prediction_score')
ORDER BY column_name;
" 2>/dev/null || echo "カラム情報の取得に失敗"

echo ""
echo "🎉 マイグレーション完了！"
echo ""
echo "📝 次のステップ:"
echo "  1. アプリケーションを再起動: docker compose restart app"
echo "  2. ブラウザでアクセス: http://localhost:8000"
echo "  3. 固定銘柄分析で新しい3つの予測値入力を試してください"
