#!/bin/bash

# 週次プロンプト生成バッチファイル
# 使用方法: ./generate_prompt.sh

echo "📈 週次株価予測プロンプト生成ツール"
echo "=================================="
echo ""

# プロンプト生成スクリプトを実行
python3 generate_weekly_prompt.py

echo ""
echo "✅ プロンプト生成完了！"
echo ""
echo "📋 次のステップ:"
echo "  1. generated/ フォルダ内の最新プロンプトファイルを開く"
echo "  2. 内容をコピーしてClaude/ChatGPT等に貼り付け"
echo "  3. 生成AIの回答を取得"
echo "  4. 株式シミュレーターで銘柄選定分析を実行"
echo "  5. 1週間後に結果を検証"
echo ""
echo "🔗 株式シミュレーター: http://localhost:8000/stock-selection"
echo ""
