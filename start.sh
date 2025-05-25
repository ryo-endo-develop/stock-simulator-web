#!/bin/bash

# データベース初期化
echo "🚀 データベースを初期化中..."
python -c "
from database import DatabaseManager
result = DatabaseManager.init_database()
if result:
    print('✅ データベース初期化完了')
else:
    print('❌ データベース初期化失敗')
    exit(1)
"

# アプリケーション起動
echo "🌐 アプリケーションを起動中..."
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
