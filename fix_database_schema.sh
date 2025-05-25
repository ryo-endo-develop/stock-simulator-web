#!/bin/bash

echo "🔧 データベーススキーマ修正スクリプト"
echo "=================================="
echo ""
echo "⚠️  注意: 既存のデータは削除されます"
echo ""

# 確認プロンプト
read -p "続行しますか？ (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ 修正をキャンセルしました"
    exit 0
fi

echo ""
echo "🛑 Docker Composeを停止中..."
docker compose down

echo ""
echo "🗑️  PostgreSQLデータボリュームを削除中..."
docker volume rm stock_simulator_web_postgres_data 2>/dev/null || echo "ボリュームが見つかりません（正常）"

echo ""
echo "🚀 Docker Composeを再起動中..."
docker compose up -d

echo ""
echo "⏳ データベースの起動を待機中..."
sleep 10

echo ""
echo "✅ データベーススキーマが更新されました"
echo ""
echo "📝 次のステップ:"
echo "  1. ブラウザでアクセス: http://localhost:8000"
echo "  2. 固定銘柄分析で新しい3つの予測値入力を試してください"
echo ""
echo "🎉 修正完了！"
