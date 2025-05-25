#!/usr/bin/env python3
"""
結果自動更新スクリプト
AI予測の実際の株価結果を更新する
使用方法: python scripts/auto_update.py <日付>
例: python scripts/auto_update.py 20250525
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database import DatabaseManager
from stock_analyzer import StockAnalyzer


class ResultUpdater:
    """結果更新クラス"""
    
    def __init__(self, date_str: str):
        self.date_str = date_str
        self.target_date = datetime.strptime(date_str, "%Y%m%d")
        
    def update_all_results(self):
        """全ての未更新結果を更新"""
        print(f"📊 {self.date_str} の結果を更新開始...")
        
        updated_count = 0
        
        # 固定銘柄分析（トヨタ）の更新
        updated_count += self.update_fixed_stock_results()
        
        # 銘柄選定分析の更新
        updated_count += self.update_selection_results()
        
        print(f"\n🎉 更新完了: {updated_count}件の結果を更新しました")
        return updated_count > 0
    
    def update_fixed_stock_results(self):
        """固定銘柄分析結果を更新"""
        print("\n📈 固定銘柄分析結果を更新中...")
        
        # 未更新のデータを取得
        fixed_df = DatabaseManager.load_fixed_stock_data()
        if fixed_df.empty:
            print("  ⚠️ 更新対象データなし")
            return 0
        
        # profit_loss=0のデータ（未更新）を対象
        pending_data = fixed_df[
            (fixed_df['profit_loss'] == 0.0) & 
            (fixed_df['execution_date'].dt.date >= self.target_date.date() - timedelta(days=7))
        ]
        
        updated_count = 0
        for _, row in pending_data.iterrows():
            try:
                # 実際の株価を取得
                buy_price, actual_buy_date = StockAnalyzer.get_closest_business_day_price(
                    row['stock_code'], row['buy_date']
                )
                sell_price, actual_sell_date = StockAnalyzer.get_closest_business_day_price(
                    row['stock_code'], row['sell_date']
                )
                
                if buy_price and sell_price:
                    # 結果を計算
                    profit_loss = sell_price - buy_price
                    return_rate = StockAnalyzer.calculate_return_rate(buy_price, sell_price)
                    prediction_accuracy = StockAnalyzer.calculate_prediction_accuracy(
                        sell_price, row['predicted_price']
                    )
                    
                    # データベースを更新
                    success = self.update_fixed_stock_record(
                        row['id'], buy_price, sell_price, actual_buy_date, actual_sell_date,
                        profit_loss, return_rate, prediction_accuracy
                    )
                    
                    if success:
                        updated_count += 1
                        print(f"  ✅ {row['stock_code']}: ¥{buy_price:,.0f} → ¥{sell_price:,.0f} ({return_rate:+.1f}%)")
                    else:
                        print(f"  ❌ {row['stock_code']}: 更新エラー")
                else:
                    print(f"  ⚠️ {row['stock_code']}: 株価取得失敗")
                    
            except Exception as e:
                print(f"  ❌ {row['stock_code']}: エラー - {str(e)}")
        
        return updated_count
    
    def update_selection_results(self):
        """銘柄選定分析結果を更新"""
        print("\n🎯 銘柄選定分析結果を更新中...")
        
        # 未更新のデータを取得
        selection_df = DatabaseManager.load_stock_selection_data()
        if selection_df.empty:
            print("  ⚠️ 更新対象データなし")
            return 0
        
        # profit_loss=0のデータ（未更新）を対象
        pending_data = selection_df[
            (selection_df['profit_loss'] == 0.0) & 
            (selection_df['execution_date'].dt.date >= self.target_date.date() - timedelta(days=7))
        ]
        
        updated_count = 0
        for _, row in pending_data.iterrows():
            try:
                # 売却日を計算（1週間後の金曜日）
                buy_date_obj = datetime.strptime(row['buy_date'], "%Y-%m-%d")
                sell_date = (buy_date_obj + timedelta(days=4)).strftime("%Y-%m-%d")
                
                # 実際の株価を取得
                buy_price, actual_buy_date = StockAnalyzer.get_closest_business_day_price(
                    row['stock_code'], row['buy_date']
                )
                sell_price, actual_sell_date = StockAnalyzer.get_closest_business_day_price(
                    row['stock_code'], sell_date
                )
                
                if buy_price and sell_price:
                    # 結果を計算
                    profit_loss = sell_price - buy_price
                    return_rate = StockAnalyzer.calculate_return_rate(buy_price, sell_price)
                    actual_period = (
                        datetime.strptime(actual_sell_date, "%Y-%m-%d") - 
                        datetime.strptime(actual_buy_date, "%Y-%m-%d")
                    ).days
                    
                    # データベースを更新
                    success = self.update_selection_record(
                        row['id'], buy_price, sell_price, actual_buy_date, actual_sell_date,
                        profit_loss, return_rate, actual_period
                    )
                    
                    if success:
                        updated_count += 1
                        print(f"  ✅ {row['stock_code']}: ¥{buy_price:,.0f} → ¥{sell_price:,.0f} ({return_rate:+.1f}%)")
                    else:
                        print(f"  ❌ {row['stock_code']}: 更新エラー")
                else:
                    print(f"  ⚠️ {row['stock_code']}: 株価取得失敗")
                    
            except Exception as e:
                print(f"  ❌ {row['stock_code']}: エラー - {str(e)}")
        
        return updated_count
    
    def update_fixed_stock_record(self, record_id, buy_price, sell_price, 
                                  actual_buy_date, actual_sell_date,
                                  profit_loss, return_rate, prediction_accuracy):
        """固定銘柄分析レコードを更新"""
        try:
            from sqlalchemy import text
            from database import SessionLocal
            
            db = SessionLocal()
            
            update_sql = text("""
                UPDATE fixed_stock_analysis 
                SET buy_price = :buy_price,
                    sell_price = :sell_price,
                    buy_date = :buy_date,
                    sell_date = :sell_date,
                    profit_loss = :profit_loss,
                    return_rate = :return_rate,
                    prediction_accuracy = :prediction_accuracy
                WHERE id = :id
            """)
            
            db.execute(update_sql, {
                'id': record_id,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'buy_date': actual_buy_date,
                'sell_date': actual_sell_date,
                'profit_loss': profit_loss,
                'return_rate': return_rate,
                'prediction_accuracy': prediction_accuracy
            })
            
            db.commit()
            db.close()
            return True
            
        except Exception as e:
            print(f"固定銘柄更新エラー: {str(e)}")
            return False
    
    def update_selection_record(self, record_id, buy_price, sell_price,
                               actual_buy_date, actual_sell_date, 
                               profit_loss, return_rate, period_days):
        """銘柄選定分析レコードを更新"""
        try:
            from sqlalchemy import text
            from database import SessionLocal
            
            db = SessionLocal()
            
            update_sql = text("""
                UPDATE stock_selection_analysis 
                SET buy_price = :buy_price,
                    sell_price = :sell_price,
                    buy_date = :buy_date,
                    sell_date = :sell_date,
                    profit_loss = :profit_loss,
                    return_rate = :return_rate,
                    period_days = :period_days
                WHERE id = :id
            """)
            
            db.execute(update_sql, {
                'id': record_id,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'buy_date': actual_buy_date,
                'sell_date': actual_sell_date,
                'profit_loss': profit_loss,
                'return_rate': return_rate,
                'period_days': period_days
            })
            
            db.commit()
            db.close()
            return True
            
        except Exception as e:
            print(f"銘柄選定更新エラー: {str(e)}")
            return False


def main():
    """メイン処理"""
    if len(sys.argv) != 2:
        print("使用方法: python scripts/auto_update.py <日付>")
        print("例: python scripts/auto_update.py 20250525")
        sys.exit(1)
    
    date_str = sys.argv[1]
    
    # 日付形式チェック
    try:
        datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        print("❌ 日付形式が正しくありません (YYYYMMDD)")
        sys.exit(1)
    
    print("🔄 結果自動更新ツール")
    print("=" * 30)
    print(f"対象日: {date_str}")
    print()
    
    # データベース初期化確認
    if not DatabaseManager.init_database():
        print("❌ データベース初期化に失敗")
        sys.exit(1)
    
    # 結果更新実行
    updater = ResultUpdater(date_str)
    success = updater.update_all_results()
    
    if success:
        print("\n✅ 結果更新が完了しました！")
        print("🌐 http://localhost:8000/history で結果を確認してください")
    else:
        print("\n⚠️ 更新対象データがありませんでした")


if __name__ == "__main__":
    main()
