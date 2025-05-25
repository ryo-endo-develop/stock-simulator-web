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
chmod +x weekly_workflow.sh

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
echo "3. 週次運用開始（金曜日）:"
echo "   ./weekly_workflow.sh prepare"
echo ""
echo "4. 予測記録（月曜日）:"
echo "   ./weekly_workflow.sh record"
echo ""
echo "5. 結果検証（金曜日）:"
echo "   ./weekly_workflow.sh verify"
echo ""
echo "📅 週次スケジュール例:"
echo "─────────────────"
echo "🔵 金曜日 17:00 | 準備フェーズ (prepare)"
echo "🟢 土日     | AIに質問・回答保存"
echo "🔴 月曜日 09:00 | 記録フェーズ (record)"
echo "🟡 金曜日 17:00 | 検証フェーズ (verify)"
echo ""
echo "📚 詳細な使用方法: scripts/README.md"
