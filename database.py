import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
import traceback

# データベース設定
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/stock_simulator")

# SQLAlchemyエンジンとセッション
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# モデル定義
class FixedStockAnalysis(Base):
    __tablename__ = "fixed_stock_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_date = Column(DateTime, nullable=False)
    model_id = Column(String, nullable=False)
    stock_code = Column(String, nullable=False)
    buy_date = Column(String, nullable=False)
    buy_price = Column(Float, nullable=False)
    sell_date = Column(String, nullable=False)
    sell_price = Column(Float, nullable=False)
    predicted_price = Column(Float, nullable=False)
    profit_loss = Column(Float, nullable=False)
    return_rate = Column(Float, nullable=False)
    prediction_accuracy = Column(Float, nullable=False)
    period_days = Column(Integer, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())

class StockSelectionAnalysis(Base):
    __tablename__ = "stock_selection_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_date = Column(DateTime, nullable=False)
    analysis_period = Column(String, nullable=False)
    model_id = Column(String, nullable=False)
    stock_code = Column(String, nullable=False)
    selection_reason = Column(Text, nullable=False)
    buy_date = Column(String, nullable=False)
    buy_price = Column(Float, nullable=False)
    sell_date = Column(String, nullable=False)
    sell_price = Column(Float, nullable=False)
    profit_loss = Column(Float, nullable=False)
    return_rate = Column(Float, nullable=False)
    period_days = Column(Integer, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())

class DatabaseManager:
    """PostgreSQLデータベース管理クラス"""
    
    @staticmethod
    def init_database():
        """データベースとテーブルを初期化"""
        try:
            Base.metadata.create_all(bind=engine)
            print("データベースを初期化しました")
            return True
        except Exception as e:
            print(f"データベース初期化エラー: {str(e)}")
            print(f"詳細エラー: {traceback.format_exc()}")
            return False
    
    @staticmethod
    def get_db():
        """データベースセッションを取得"""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    @staticmethod
    def save_fixed_stock_analysis(data: Dict) -> bool:
        """固定銘柄分析データを保存"""
        try:
            db = SessionLocal()
            
            analysis = FixedStockAnalysis(
                execution_date=data['execution_date'],
                model_id=data['model_id'],
                stock_code=data['stock_code'],
                buy_date=data['buy_date'],
                buy_price=data['buy_price'],
                sell_date=data['sell_date'],
                sell_price=data['sell_price'],
                predicted_price=data['predicted_price'],
                profit_loss=data['profit_loss'],
                return_rate=data['return_rate'],
                prediction_accuracy=data['prediction_accuracy'],
                period_days=data['period_days'],
                notes=data['notes']
            )
            
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            db.close()
            
            print(f"固定銘柄分析データを保存しました (ID: {analysis.id})")
            return True
        except Exception as e:
            print(f"固定銘柄分析データ保存エラー: {str(e)}")
            print(f"詳細エラー: {traceback.format_exc()}")
            return False
    
    @staticmethod
    def save_stock_selection_analysis(data: Dict) -> bool:
        """銘柄選定分析データを保存"""
        try:
            db = SessionLocal()
            
            analysis = StockSelectionAnalysis(
                execution_date=data['execution_date'],
                analysis_period=data['analysis_period'],
                model_id=data['model_id'],
                stock_code=data['stock_code'],
                selection_reason=data['selection_reason'],
                buy_date=data['buy_date'],
                buy_price=data['buy_price'],
                sell_date=data['sell_date'],
                sell_price=data['sell_price'],
                profit_loss=data['profit_loss'],
                return_rate=data['return_rate'],
                period_days=data['period_days'],
                notes=data['notes']
            )
            
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            db.close()
            
            print(f"銘柄選定分析データを保存しました (ID: {analysis.id})")
            return True
        except Exception as e:
            print(f"銘柄選定分析データ保存エラー: {str(e)}")
            print(f"詳細エラー: {traceback.format_exc()}")
            return False
    
    @staticmethod
    def load_fixed_stock_data() -> pd.DataFrame:
        """固定銘柄分析データを読み込み"""
        try:
            db = SessionLocal()
            analyses = db.query(FixedStockAnalysis).order_by(FixedStockAnalysis.created_at.desc()).all()
            db.close()
            
            if not analyses:
                return pd.DataFrame()
            
            data = []
            for analysis in analyses:
                data.append({
                    'id': analysis.id,
                    'execution_date': analysis.execution_date,
                    'model_id': analysis.model_id,
                    'stock_code': analysis.stock_code,
                    'buy_date': analysis.buy_date,
                    'buy_price': analysis.buy_price,
                    'sell_date': analysis.sell_date,
                    'sell_price': analysis.sell_price,
                    'predicted_price': analysis.predicted_price,
                    'profit_loss': analysis.profit_loss,
                    'return_rate': analysis.return_rate,
                    'prediction_accuracy': analysis.prediction_accuracy,
                    'period_days': analysis.period_days,
                    'notes': analysis.notes,
                    'created_at': analysis.created_at
                })
            
            return pd.DataFrame(data)
        except Exception as e:
            print(f"固定銘柄分析データ読み込みエラー: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def load_stock_selection_data() -> pd.DataFrame:
        """銘柄選定分析データを読み込み"""
        try:
            db = SessionLocal()
            analyses = db.query(StockSelectionAnalysis).order_by(StockSelectionAnalysis.created_at.desc()).all()
            db.close()
            
            if not analyses:
                return pd.DataFrame()
            
            data = []
            for analysis in analyses:
                data.append({
                    'id': analysis.id,
                    'execution_date': analysis.execution_date,
                    'analysis_period': analysis.analysis_period,
                    'model_id': analysis.model_id,
                    'stock_code': analysis.stock_code,
                    'selection_reason': analysis.selection_reason,
                    'buy_date': analysis.buy_date,
                    'buy_price': analysis.buy_price,
                    'sell_date': analysis.sell_date,
                    'sell_price': analysis.sell_price,
                    'profit_loss': analysis.profit_loss,
                    'return_rate': analysis.return_rate,
                    'period_days': analysis.period_days,
                    'notes': analysis.notes,
                    'created_at': analysis.created_at
                })
            
            return pd.DataFrame(data)
        except Exception as e:
            print(f"銘柄選定分析データ読み込みエラー: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def get_summary_stats():
        """サマリー統計を取得"""
        try:
            fixed_df = DatabaseManager.load_fixed_stock_data()
            selection_df = DatabaseManager.load_stock_selection_data()
            
            total_analyses = len(fixed_df) + len(selection_df)
            
            # 勝率計算
            all_returns = []
            if not fixed_df.empty:
                all_returns.extend(fixed_df["return_rate"].tolist())
            if not selection_df.empty:
                all_returns.extend(selection_df["return_rate"].tolist())
            
            win_rate = 0
            if all_returns:
                win_rate = sum(1 for r in all_returns if r > 0) / len(all_returns) * 100
            
            # 平均予測精度
            avg_accuracy = 0
            if not fixed_df.empty:
                avg_accuracy = fixed_df["prediction_accuracy"].mean()
            
            # ユニークモデル数
            unique_models = set()
            if not fixed_df.empty:
                unique_models.update(fixed_df["model_id"].unique())
            if not selection_df.empty:
                unique_models.update(selection_df["model_id"].unique())
            
            return {
                "total_analyses": total_analyses,
                "win_rate": round(win_rate, 1),
                "avg_accuracy": round(avg_accuracy, 1),
                "unique_models": len(unique_models)
            }
        except Exception as e:
            print(f"サマリー統計取得エラー: {str(e)}")
            return {
                "total_analyses": 0,
                "win_rate": 0,
                "avg_accuracy": 0,
                "unique_models": 0
            }
