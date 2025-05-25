#!/bin/bash

# 週次運用支援スクリプト
# 使用方法: ./weekly_workflow.sh [prepare|record|verify]

echo "📅 週次運用支援ツール"
echo "==================="
echo ""

# 引数チェック
PHASE=${1:-"help"}

case $PHASE in
    "prepare")
        echo "🔄 【準備フェーズ】次週の予測準備"
        echo "==============================="
        echo ""
        
        # 1. プロンプト生成
        echo "1️⃣ プロンプト生成中..."
        cd prompts/
        python generate_weekly_prompt.py
        cd ..
        echo ""
        
        # 2. 回答保存用ディレクトリ作成
        echo "2️⃣ 回答保存ディレクトリ作成中..."
        TODAY=$(date +%Y%m%d)
        mkdir -p ai_responses/$TODAY
        
        # テンプレートをコピー
        cp ai_responses/response_template.md ai_responses/$TODAY/claude_response.md
        cp ai_responses/response_template.md ai_responses/$TODAY/chatgpt_response.md
        cp ai_responses/response_template.md ai_responses/$TODAY/gemini_response.md
        
        echo "✅ 準備完了！"
        echo ""
        echo "📋 次のステップ:"
        echo "  1. generated/weekly_prompt_$TODAY.md を開く"
        echo "  2. Claude, ChatGPT, Geminiに質問"
        echo "  3. 回答をai_responses/$TODAY/の各ファイルに保存"
        echo ""
        echo "🔗 プロンプトファイル:"
        echo "  $(pwd)/prompts/generated/weekly_prompt_$TODAY.md"
        echo ""
        echo "📁 回答保存先:"
        echo "  $(pwd)/ai_responses/$TODAY/"
        ;;
        
    "record")
        echo "📝 【記録フェーズ】予測をシステムに記録"
        echo "====================================="
        echo ""
        
        # アプリケーション起動確認
        if ! curl -s http://localhost:8000 > /dev/null; then
            echo "⚠️  アプリケーションが起動していません"
            echo "   docker-compose up -d で起動してください"
            echo ""
            read -p "アプリケーションを起動しますか？ (y/n): " start_app
            if [ "$start_app" = "y" ]; then
                docker-compose up -d
                echo "アプリケーション起動中... 30秒待機"
                sleep 30
            else
                echo "❌ 記録フェーズを中断しました"
                exit 1
            fi
        fi
        
        echo "✅ アプリケーションが起動中です"
        echo ""
        echo "📊 データベース状況:"
        ./scripts/db_check.sh | tail -n 5
        echo ""
        echo "🌐 ブラウザでアクセスしてください:"
        echo "  http://localhost:8000"
        echo ""
        echo "📋 記録手順:"
        echo "  1. 銘柄選定分析で各AIの上位5銘柄を記録"
        echo "  2. 固定銘柄分析でトヨタ株予測を記録"
        echo "  3. 合計: 銘柄選定15件 + 固定銘柄3件 = 18件"
        echo ""
        
        # 回答ファイルの確認
        TODAY=$(date +%Y%m%d)
        if [ -d "ai_responses/$TODAY" ]; then
            echo "📁 今日の回答ファイル:"
            ls -la ai_responses/$TODAY/
        else
            echo "⚠️  ai_responses/$TODAY が見つかりません"
            echo "   prepare フェーズを先に実行してください"
        fi
        ;;
        
    "verify")
        echo "🔍 【検証フェーズ】週次結果の確認"
        echo "==============================="
        echo ""
        
        # 1. 結果確認
        echo "1️⃣ 週次結果を確認中..."
        echo ""
        echo "📊 今週の実績サマリー:"
        ./scripts/db_show_all.sh | tail -n 15
        echo ""
        
        # 2. CSVエクスポート
        echo "2️⃣ CSVエクスポート実行中..."
        ./scripts/db_export_csv.sh all
        echo ""
        
        # 3. バックアップ作成
        echo "3️⃣ 週次バックアップ作成中..."
        ./scripts/db_dump.sh full
        echo ""
        
        # 4. 履歴分析ページを開く
        echo "4️⃣ 履歴分析ページを開いています..."
        echo ""
        echo "🌐 ブラウザでアクセスしてください:"
        echo "  http://localhost:8000/history"
        echo ""
        echo "📈 確認ポイント:"
        echo "  • モデル別パフォーマンスランキング"
        echo "  • 今週の勝率・精度"
        echo "  • 累計統計の変化"
        echo ""
        
        # 5. 次週の準備案内
        echo "5️⃣ 次週の準備:"
        echo "  ./weekly_workflow.sh prepare"
        ;;
        
    "help"|*)
        echo "🚀 週次運用ワークフロー"
        echo ""
        echo "使用方法:"
        echo "  ./weekly_workflow.sh <フェーズ>"
        echo ""
        echo "📋 利用可能なフェーズ:"
        echo ""
        echo "🔄 prepare  - 【金曜夕方】次週予測の準備"
        echo "   • プロンプト自動生成"
        echo "   • 回答保存ディレクトリ作成"
        echo "   • テンプレートファイル準備"
        echo ""
        echo "📝 record   - 【月曜朝】予測をシステムに記録"
        echo "   • アプリケーション起動確認"
        echo "   • データベース状況確認"
        echo "   • 記録手順の案内"
        echo ""
        echo "🔍 verify   - 【金曜夕方】週次結果の検証"
        echo "   • 実績サマリー表示"
        echo "   • CSVエクスポート実行"
        echo "   • バックアップ作成"
        echo "   • パフォーマンス分析案内"
        echo ""
        echo "💡 推奨スケジュール:"
        echo "  金曜夕方: ./weekly_workflow.sh prepare"
        echo "  月曜朝  : ./weekly_workflow.sh record"
        echo "  金曜夕方: ./weekly_workflow.sh verify"
        echo ""
        echo "🔗 関連コマンド:"
        echo "  ./scripts/db_check.sh     - DB状況確認"
        echo "  ./scripts/db_show_all.sh  - 全データ表示"
        ;;
esac
