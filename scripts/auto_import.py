#!/usr/bin/env python3
"""
AI回答自動解析・投入スクリプト
使用方法: python scripts/auto_import.py <日付>
例: python scripts/auto_import.py 20250525
"""

import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database import DatabaseManager


class AIResponseParser:
    """AI回答ファイル解析クラス"""
    
    def __init__(self, date_str: str):
        self.date_str = date_str
        self.responses_dir = project_root / "ai_responses" / date_str
        self.predictions = {}
        
    def parse_all_responses(self):
        """全AI回答ファイルを解析"""
        if not self.responses_dir.exists():
            print(f"❌ 回答ディレクトリが見つかりません: {self.responses_dir}")
            return False
            
        # AI別の回答ファイルを解析
        models = {
            "claude_response.md": "claude-3-sonnet",
            "chatgpt_response.md": "chatgpt-4", 
            "gemini_response.md": "gemini-pro"
        }
        
        for filename, model_id in models.items():
            filepath = self.responses_dir / filename
            if filepath.exists():
                print(f"📖 {filename} を解析中...")
                prediction = self.parse_single_response(filepath, model_id)
                if prediction:
                    self.predictions[model_id] = prediction
                    print(f"✅ {model_id} の解析完了")
                else:
                    print(f"⚠️ {model_id} の解析に失敗")
            else:
                print(f"⚠️ {filename} が見つかりません")
                
        return len(self.predictions) > 0
    
    def parse_single_response(self, filepath: Path, model_id: str) -> dict:
        """単一AI回答ファイルを解析"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 銘柄選定（1位〜5位）を抽出
            stocks = self.extract_top_stocks(content)
            
            # トヨタ予測を抽出  
            toyota_prediction = self.extract_toyota_prediction(content)
            
            return {
                "model_id": model_id,
                "stocks": stocks,
                "toyota": toyota_prediction,
                "raw_content": content
            }
            
        except Exception as e:
            print(f"ファイル解析エラー ({filepath}): {str(e)}")
            return None
    
    def extract_top_stocks(self, content: str) -> list:
        """上位5銘柄を抽出"""
        stocks = []
        
        # 複数のパターンで銘柄情報を検索
        patterns = [
            r'【(\d+)位】.*?銘柄コード[：:]?\s*(\d{4}).*?企業名[：:]?\s*(.*?)(?=\n)',
            r'(\d+)位.*?(\d{4}).*?(.*?)(?=\n)',
            r'銘柄コード[：:]?\s*(\d{4}).*?企業名[：:]?\s*(.*?)(?=\n)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if len(match) == 3:
                    rank, code, company = match
                    rank_num = int(rank) if rank.isdigit() else len(stocks) + 1
                elif len(match) == 2:
                    code, company = match
                    rank_num = len(stocks) + 1
                else:
                    continue
                    
                if rank_num <= 5 and len(code) == 4 and code.isdigit():
                    # 選定理由を抽出
                    reason = self.extract_selection_reason(content, rank_num, code)
                    
                    stocks.append({
                        "rank": rank_num,
                        "stock_code": code,
                        "company_name": company.strip(),
                        "selection_reason": reason
                    })
                    
                if len(stocks) >= 5:
                    break
            if len(stocks) >= 5:
                break
        
        return sorted(stocks, key=lambda x: x["rank"])[:5]
    
    def extract_selection_reason(self, content: str, rank: int, stock_code: str) -> str:
        """選定理由を抽出"""
        try:
            # 銘柄コード周辺のテキストを抽出
            code_pattern = rf'{stock_code}.*?(?=\d{{4}}|\n\n|\Z)'
            section_match = re.search(code_pattern, content, re.DOTALL)
            
            if section_match:
                section = section_match.group(0)
                # 理由部分を抽出
                reason_lines = []
                lines = section.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('**'):
                        reason_lines.append(line)
                        if len(' '.join(reason_lines)) > 200:
                            break
                
                if reason_lines:
                    return ' '.join(reason_lines)[:300]
            
            return f"{stock_code} 選定理由（回答ファイル参照）"
            
        except Exception as e:
            return f"{stock_code} 選定理由抽出エラー"
    
    def extract_toyota_prediction(self, content: str) -> dict:
        """トヨタ株予測を抽出"""
        try:
            # 価格パターンを検索
            price_patterns = [
                r'週末終値予想[：:]?\s*([0-9,]+)円',
                r'終値予想[：:]?\s*([0-9,]+)円',
                r'予想.*?([0-9,]+)円'
            ]
            
            predicted_price = 3000.0
            for pattern in price_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    price_str = match.group(1).replace(',', '')
                    try:
                        predicted_price = float(price_str)
                        break
                    except:
                        continue
            
            return {
                "predicted_price": predicted_price,
                "notes": "AI自動解析による予測"
            }
            
        except Exception as e:
            return {
                "predicted_price": 3000.0,
                "notes": "予測抽出エラー"
            }


class AutoImporter:
    """自動投入クラス"""
    
    def __init__(self, date_str: str):
        self.date_str = date_str
        self.parser = AIResponseParser(date_str)
        
    def import_all_predictions(self):
        """全予測をデータベースに投入"""
        print(f"🤖 {self.date_str} のAI回答を解析・投入開始...")
        
        # AI回答を解析
        if not self.parser.parse_all_responses():
            print("❌ AI回答の解析に失敗しました")
            return False
        
        # 購入日を設定（指定日の次の月曜日）
        buy_date = self.calculate_next_monday(self.date_str)
        execution_date = datetime.now()
        
        total_imported = 0
        
        # 各AIの予測を投入
        for model_id, prediction in self.parser.predictions.items():
            print(f"\n📝 {model_id} のデータを投入中...")
            
            # 銘柄選定分析を投入
            for i, stock in enumerate(prediction["stocks"]):
                success = self.import_stock_selection(
                    execution_date=execution_date,
                    model_id=model_id,
                    stock_data=stock,
                    buy_date=buy_date
                )
                if success:
                    total_imported += 1
                    print(f"  ✅ 銘柄選定: {stock['stock_code']} ({stock['rank']}位)")
                else:
                    print(f"  ❌ 銘柄選定エラー: {stock['stock_code']}")
            
            # トヨタ固定銘柄分析を投入
            if prediction["toyota"]:
                success = self.import_toyota_prediction(
                    execution_date=execution_date,
                    model_id=model_id,
                    toyota_data=prediction["toyota"],
                    buy_date=buy_date
                )
                if success:
                    total_imported += 1
                    print(f"  ✅ トヨタ予測: ¥{prediction['toyota']['predicted_price']:,.0f}")
                else:
                    print(f"  ❌ トヨタ予測エラー")
        
        print(f"\n🎉 投入完了: {total_imported}件のデータを投入しました")
        return total_imported > 0
    
    def calculate_next_monday(self, date_str: str) -> str:
        """指定日の次の月曜日を計算"""
        try:
            base_date = datetime.strptime(date_str, "%Y%m%d")
            days_ahead = 7 - base_date.weekday()  # 月曜日=0
            if days_ahead <= 0:
                days_ahead += 7
            next_monday = base_date + timedelta(days=days_ahead)
            return next_monday.strftime("%Y-%m-%d")
        except:
            # フォールバック: 来週月曜日
            today = datetime.now()
            days_ahead = 7 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_monday = today + timedelta(days=days_ahead)
            return next_monday.strftime("%Y-%m-%d")
    
    def import_stock_selection(self, execution_date, model_id, stock_data, buy_date):
        """銘柄選定分析を投入"""
        try:
            # ダミーの価格データ（実際の運用では1週間後に更新）
            save_data = {
                "execution_date": execution_date,
                "analysis_period": "1週間",
                "model_id": model_id,
                "stock_code": stock_data["stock_code"],
                "selection_reason": stock_data["selection_reason"],
                "buy_date": buy_date,
                "buy_price": 1000.0,  # 後で更新される
                "sell_date": buy_date,  # 後で更新される
                "sell_price": 1000.0,  # 後で更新される
                "profit_loss": 0.0,  # 後で更新される
                "return_rate": 0.0,  # 後で更新される
                "period_days": 5,  # 1週間想定
                "notes": f"AI自動投入 - {stock_data['rank']}位選定"
            }
            
            return DatabaseManager.save_stock_selection_analysis(save_data)
            
        except Exception as e:
            print(f"銘柄選定投入エラー: {str(e)}")
            return False
    
    def import_toyota_prediction(self, execution_date, model_id, toyota_data, buy_date):
        """トヨタ固定銘柄分析を投入"""
        try:
            # 1週間後の売却日を計算
            buy_date_obj = datetime.strptime(buy_date, "%Y-%m-%d")
            sell_date = (buy_date_obj + timedelta(days=4)).strftime("%Y-%m-%d")  # 金曜日
            
            save_data = {
                "execution_date": execution_date,
                "model_id": model_id,
                "stock_code": "7203",
                "buy_date": buy_date,
                "buy_price": 3000.0,  # 後で更新される
                "sell_date": sell_date,
                "sell_price": 3000.0,  # 後で更新される  
                "predicted_price": toyota_data["predicted_price"],
                "profit_loss": 0.0,  # 後で更新される
                "return_rate": 0.0,  # 後で更新される
                "prediction_accuracy": 0.0,  # 後で更新される
                "period_days": 5,
                "notes": f"AI自動投入 - {toyota_data['notes']}"
            }
            
            return DatabaseManager.save_fixed_stock_analysis(save_data)
            
        except Exception as e:
            print(f"トヨタ予測投入エラー: {str(e)}")
            return False


def main():
    """メイン処理"""
    if len(sys.argv) != 2:
        print("使用方法: python scripts/auto_import.py <日付>")
        print("例: python scripts/auto_import.py 20250525")
        sys.exit(1)
    
    date_str = sys.argv[1]
    
    # 日付形式チェック
    try:
        datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        print("❌ 日付形式が正しくありません (YYYYMMDD)")
        sys.exit(1)
    
    print("🚀 AI回答自動解析・投入ツール")
    print("=" * 40)
    print(f"対象日: {date_str}")
    print()
    
    # データベース初期化確認
    if not DatabaseManager.init_database():
        print("❌ データベース初期化に失敗")
        sys.exit(1)
    
    # 自動投入実行
    importer = AutoImporter(date_str)
    success = importer.import_all_predictions()
    
    if success:
        print("\n✅ 自動投入が完了しました！")
        print("🌐 http://localhost:8000/history で結果を確認してください")
    else:
        print("\n❌ 自動投入に失敗しました")
        sys.exit(1)


if __name__ == "__main__":
    main()
