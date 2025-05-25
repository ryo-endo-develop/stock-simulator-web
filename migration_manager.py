"""
データベースマイグレーション管理システム
"""

import os
from datetime import datetime
from typing import List, Dict
import traceback
from sqlalchemy import text, Column, Integer, String, DateTime, Boolean
from sqlalchemy.exc import ProgrammingError

from database import engine, SessionLocal, Base


class Migration(Base):
    """マイグレーション履歴管理テーブル"""
    __tablename__ = "migrations"
    
    id = Column(Integer, primary_key=True, index=True)
    migration_name = Column(String, unique=True, nullable=False)
    executed_at = Column(DateTime, default=datetime.now)
    success = Column(Boolean, default=True)


class MigrationManager:
    """マイグレーション管理クラス"""
    
    def __init__(self):
        self.migrations_dir = "migrations"
        self.ensure_migrations_table()
        
    def ensure_migrations_table(self):
        """マイグレーション管理テーブルの存在確認・作成"""
        try:
            # マイグレーション管理テーブルのみ作成
            Migration.__table__.create(engine, checkfirst=True)
            print("✅ マイグレーション管理テーブル準備完了")
        except Exception as e:
            print(f"マイグレーション管理テーブル作成エラー: {str(e)}")
    
    def get_executed_migrations(self) -> List[str]:
        """実行済みマイグレーション一覧を取得"""
        try:
            db = SessionLocal()
            migrations = db.query(Migration).filter(Migration.success == True).all()
            db.close()
            return [m.migration_name for m in migrations]
        except:
            return []
    
    def execute_migration(self, migration_name: str, sql_commands: List[str]) -> bool:
        """マイグレーションを実行"""
        try:
            db = SessionLocal()
            
            print(f"🔄 マイグレーション実行中: {migration_name}")
            
            # SQLコマンドを順次実行
            for sql in sql_commands:
                if sql.strip():
                    db.execute(text(sql))
            
            # マイグレーション履歴に記録
            migration_record = Migration(
                migration_name=migration_name,
                executed_at=datetime.now(),
                success=True
            )
            db.add(migration_record)
            db.commit()
            db.close()
            
            print(f"✅ マイグレーション完了: {migration_name}")
            return True
            
        except Exception as e:
            print(f"❌ マイグレーション失敗 {migration_name}: {str(e)}")
            print(f"詳細エラー: {traceback.format_exc()}")
            
            # 失敗記録
            try:
                db = SessionLocal()
                migration_record = Migration(
                    migration_name=migration_name,
                    executed_at=datetime.now(),
                    success=False
                )
                db.add(migration_record)
                db.commit()
                db.close()
            except:
                pass
                
            return False
    
    def run_pending_migrations(self):
        """未実行のマイグレーションを実行"""
        executed_migrations = self.get_executed_migrations()
        
        # 定義済みマイグレーション
        migrations = self.get_all_migrations()
        
        pending_count = 0
        for migration_name, sql_commands in migrations.items():
            if migration_name not in executed_migrations:
                if self.execute_migration(migration_name, sql_commands):
                    pending_count += 1
                else:
                    print(f"⚠️  マイグレーション {migration_name} の実行に失敗しました")
                    break
        
        if pending_count > 0:
            print(f"🎉 {pending_count}個のマイグレーションを実行しました")
        else:
            print("📋 実行すべきマイグレーションはありません")
    
    def get_all_migrations(self) -> Dict[str, List[str]]:
        """全マイグレーション定義を取得"""
        return {
            "001_add_three_predictions": [
                # 3つの予測値カラムを追加
                """
                ALTER TABLE fixed_stock_analysis 
                ADD COLUMN IF NOT EXISTS predicted_high FLOAT;
                """,
                """
                ALTER TABLE fixed_stock_analysis 
                ADD COLUMN IF NOT EXISTS predicted_low FLOAT;
                """,
                """
                ALTER TABLE fixed_stock_analysis 
                ADD COLUMN IF NOT EXISTS predicted_close FLOAT;
                """,
                # 既存のpredicted_priceからpredicted_closeにデータをコピー
                """
                UPDATE fixed_stock_analysis 
                SET predicted_close = predicted_price 
                WHERE predicted_close IS NULL;
                """,
            ],
            
            "002_add_actual_high_low": [
                # 実際の最高・最安値カラムを追加
                """
                ALTER TABLE fixed_stock_analysis 
                ADD COLUMN IF NOT EXISTS actual_high FLOAT;
                """,
                """
                ALTER TABLE fixed_stock_analysis 
                ADD COLUMN IF NOT EXISTS actual_low FLOAT;
                """,
            ],
            
            "003_add_prediction_accuracies": [
                # 新しい精度指標カラムを追加
                """
                ALTER TABLE fixed_stock_analysis 
                ADD COLUMN IF NOT EXISTS high_prediction_accuracy FLOAT;
                """,
                """
                ALTER TABLE fixed_stock_analysis 
                ADD COLUMN IF NOT EXISTS low_prediction_accuracy FLOAT;
                """,
                """
                ALTER TABLE fixed_stock_analysis 
                ADD COLUMN IF NOT EXISTS overall_prediction_score FLOAT;
                """,
            ],
            
            "004_set_not_null_constraints": [
                # predicted_closeをNOT NULLに設定（データ移行後）
                """
                ALTER TABLE fixed_stock_analysis 
                ALTER COLUMN predicted_close SET NOT NULL;
                """,
            ]
        }
    
    def rollback_migration(self, migration_name: str):
        """マイグレーションをロールバック（必要に応じて実装）"""
        print(f"⚠️  ロールバック機能は未実装: {migration_name}")
        print("データバックアップから復元することを推奨します")


# 使用例
if __name__ == "__main__":
    manager = MigrationManager()
    manager.run_pending_migrations()
