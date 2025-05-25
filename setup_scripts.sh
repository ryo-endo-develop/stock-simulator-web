#!/bin/bash

# スクリプト初期化
# 使用方法: ./setup_scripts.sh

echo "🛠️  データベース管理スクリプト初期化"
echo "================================="
echo ""

# 現在のディレクトリ確認
if [ ! -d "scripts" ]; then
    echo "❌ scriptsディレクトリが見つかりません"
    echo "   プロジェクトルートディレクトリで実行してください"
    exit 1
fi

echo "📁 scriptsディレクトリを確認しました"

# 実行権限を付与
echo "🔧 スクリプトに実行権限を付与中..."

chmod +x scripts/*.sh

echo "✅ 実行権限付与完了"

echo ""
echo "📋 利用可能なスクリプト:"
echo "----------------------"
ls -la scripts/*.sh

echo ""
echo "🎯 推奨最初のステップ:"
echo "--------------------"
echo "1. データベース状況確認:"
echo "   ./scripts/db_check.sh"
echo ""
echo "2. 全データ確認:"
echo "   ./scripts/db_show_all.sh"
echo ""
echo "3. CSVエクスポート:"
echo "   ./scripts/db_export_csv.sh all"
echo ""
echo "📚 詳細な使用方法: scripts/README.md"
