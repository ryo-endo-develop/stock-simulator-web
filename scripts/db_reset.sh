#!/bin/bash

# データベースリセットスクリプト
# 使用方法: ./db_reset.sh

echo "⚠️  PostgreSQL データベースリセット"
echo "=================================="
echo ""
echo "このスクリプトは以下のデータを削除します:"
echo "  • 固定銘柄分析の全データ"
echo "  • 銘柄選定分析の全データ"
echo "  • AIモデルデータ（再投入されます）"
echo ""
echo "💾 推奨: リセット前にバックアップを取得してください"
echo "   ./scripts/db_dump.sh full"
echo ""
echo "🆆 代替手段: マイグレーションでデータを保持"
echo "   ./scripts/run_migrations.sh"
echo ""

# 確認プロンプト
read -p "本当にデータベースをリセットしますか？ (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ リセットをキャンセルしました"
    exit 0
fi

echo ""
echo "🔄 データベースリセット開始..."

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

echo "📊 リセット前のデータ確認:"
echo "------------------------"

# 現在のレコード数を表示
FIXED_COUNT=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM fixed_stock_analysis;")
SELECTION_COUNT=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM stock_selection_analysis;")
AI_MODELS_COUNT=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM ai_models;")

echo "固定銘柄分析: $FIXED_COUNT 件"
echo "銘柄選定分析: $SELECTION_COUNT 件"
echo "AIモデル: $AI_MODELS_COUNT 件"

echo ""
echo "🗑️  データ削除中..."

# データを削除
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
DROP TABLE IF EXISTS fixed_stock_analysis CASCADE;
DROP TABLE IF EXISTS stock_selection_analysis CASCADE;
DROP TABLE IF EXISTS ai_models CASCADE;
"

echo "✅ テーブル削除完了"

echo ""
echo "🔄 AIモデル初期データ再投入中..."

# テーブルを再作成してAIモデルの初期データを再投入
echo "🛠️  テーブルを再作成中..."
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
CREATE TABLE IF NOT EXISTS ai_models (
    id SERIAL PRIMARY KEY,
    model_code VARCHAR UNIQUE NOT NULL,
    model_name VARCHAR NOT NULL,
    provider VARCHAR NOT NULL,
    model_type VARCHAR NOT NULL,
    version VARCHAR,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fixed_stock_analysis (
    id SERIAL PRIMARY KEY,
    execution_date TIMESTAMP NOT NULL,
    model_id VARCHAR NOT NULL,
    stock_code VARCHAR NOT NULL,
    buy_date VARCHAR NOT NULL,
    buy_price FLOAT NOT NULL,
    sell_date VARCHAR NOT NULL,
    sell_price FLOAT NOT NULL,
    
    -- 3つの予測値
    predicted_high FLOAT,
    predicted_low FLOAT,
    predicted_close FLOAT NOT NULL,
    
    -- 実際の値
    actual_high FLOAT,
    actual_low FLOAT,
    
    -- 下位互換性
    predicted_price FLOAT NOT NULL,
    
    profit_loss FLOAT NOT NULL,
    return_rate FLOAT NOT NULL,
    prediction_accuracy FLOAT NOT NULL,
    
    -- 新しい精度指標
    high_prediction_accuracy FLOAT,
    low_prediction_accuracy FLOAT,
    overall_prediction_score FLOAT,
    
    period_days INTEGER NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stock_selection_analysis (
    id SERIAL PRIMARY KEY,
    execution_date TIMESTAMP NOT NULL,
    analysis_period VARCHAR NOT NULL,
    model_id VARCHAR NOT NULL,
    stock_code VARCHAR NOT NULL,
    selection_reason TEXT NOT NULL,
    buy_date VARCHAR NOT NULL,
    buy_price FLOAT NOT NULL,
    sell_date VARCHAR NOT NULL,
    sell_price FLOAT NOT NULL,
    profit_loss FLOAT NOT NULL,
    return_rate FLOAT NOT NULL,
    period_days INTEGER NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
"

echo "✅ テーブル再作成完了"

# AIモデルの初期データを再投入
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
INSERT INTO ai_models (model_code, model_name, provider, model_type, version, description, is_active) VALUES
('gpt-4', 'GPT-4', 'OpenAI', 'GPT-4', 'Base', 'OpenAIの最新大規模言語モデル', true),
('gpt-4-turbo', 'GPT-4 Turbo', 'OpenAI', 'GPT-4', 'Turbo', 'GPT-4の高速版', true),
('gpt-3.5-turbo', 'GPT-3.5 Turbo', 'OpenAI', 'GPT-3.5', 'Turbo', 'OpenAIのコスト効率の高いモデル', true),
('chatgpt-4', 'ChatGPT-4', 'OpenAI', 'ChatGPT', '4', 'ChatGPTのGPT-4ベース版', true),
('claude-3-opus', 'Claude 3 Opus', 'Anthropic', 'Claude-3', 'Opus', 'Claude 3シリーズの最高性能モデル', true),
('claude-3-sonnet', 'Claude 3 Sonnet', 'Anthropic', 'Claude-3', 'Sonnet', 'Claude 3シリーズのバランス型モデル', true),
('claude-3-haiku', 'Claude 3 Haiku', 'Anthropic', 'Claude-3', 'Haiku', 'Claude 3シリーズの高速モデル', true),
('claude-2', 'Claude 2', 'Anthropic', 'Claude-2', 'Base', 'Anthropicの前世代モデル', true),
('gemini-pro', 'Gemini Pro', 'Google', 'Gemini', 'Pro', 'Googleの最新マルチモーダルモデル', true),
('gemini-ultra', 'Gemini Ultra', 'Google', 'Gemini', 'Ultra', 'Geminiシリーズの最高性能モデル', true),
('bard', 'Bard', 'Google', 'Bard', 'Base', 'Googleの会話型AI', true),
('bing-chat', 'Bing Chat', 'Microsoft', 'Bing', 'Base', 'Microsoft Bingの会話型AI', true),
('copilot', 'Microsoft Copilot', 'Microsoft', 'Copilot', 'Base', 'MicrosoftのAIアシスタント', true),
('llama-2', 'Llama 2', 'Meta', 'Llama', '2', 'Metaのオープンソース大規模言語モデル', true),
('palm-2', 'PaLM 2', 'Google', 'PaLM', '2', 'Googleの前世代大規模言語モデル', true),
('custom', 'その他', 'Various', 'Custom', 'N/A', 'リストにないその他のモデル', true);
"

echo "✅ AIモデル初期データ投入完了"

echo ""
echo "📊 リセット後のデータ確認:"
echo "------------------------"

# リセット後のレコード数を表示
FIXED_COUNT_AFTER=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM fixed_stock_analysis;")
SELECTION_COUNT_AFTER=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM stock_selection_analysis;")
AI_MODELS_COUNT_AFTER=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM ai_models;")

echo "固定銘柄分析: $FIXED_COUNT_AFTER 件"
echo "銘柄選定分析: $SELECTION_COUNT_AFTER 件"
echo "AIモデル: $AI_MODELS_COUNT_AFTER 件"

echo ""
echo "🎉 データベースリセット完了！"
echo ""
echo "📝 次のステップ:"
echo "  1. アプリケーションを再起動: docker compose restart app"
echo "  2. ブラウザでアクセス: http://localhost:8000"
echo "  3. 新しい分析データを登録してください"
