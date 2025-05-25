#!/bin/bash

# 自動化スクリプト用の実行権限付与
echo "🚀 自動化スクリプトのセットアップ"
echo "================================"
echo ""

# Pythonスクリプトは権限不要だが、確認
echo "📝 Pythonスクリプトを確認..."
ls -la scripts/auto_*.py

echo ""
echo "✅ 自動化スクリプトの準備完了！"
echo ""
echo "📋 使用方法:"
echo "  ./weekly_workflow.sh record   # AI回答を自動投入"
echo "  ./weekly_workflow.sh verify   # 結果を自動更新・検証"
echo ""
echo "💡 手動実行も可能:"
echo "  python scripts/auto_import.py 20250525   # 特定日の自動投入"
echo "  python scripts/auto_update.py 20250525   # 特定日の結果更新"
