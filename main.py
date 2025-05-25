from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime, timedelta
from typing import Optional
import uvicorn

from database import DatabaseManager
from stock_analyzer import StockAnalyzer

# FastAPIアプリケーション
app = FastAPI(title="LLM投資アイデア検証ツール")

# テンプレート設定
templates = Jinja2Templates(directory="templates")

# データベース初期化
@app.on_event("startup")
async def startup_event():
    print("🚀 アプリケーション起動中...")
    result = DatabaseManager.init_database()
    if result:
        print("✅ データベース初期化完了")
    else:
        print("❌ データベース初期化に問題が発生しました")

# ルート定義
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """ホームページ"""
    stats = DatabaseManager.get_summary_stats()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats
    })

@app.get("/fixed-stock", response_class=HTMLResponse)
async def fixed_stock_form(request: Request, success: Optional[str] = None, error: Optional[str] = None):
    """固定銘柄分析フォーム"""
    return templates.TemplateResponse("fixed_stock.html", {
        "request": request,
        "success_message": success,
        "error_message": error
    })

@app.post("/fixed-stock")
async def fixed_stock_submit(
    request: Request,
    model_id: str = Form(...),
    stock_code: str = Form(...),
    predicted_price: float = Form(...),
    buy_date: str = Form(...),
    sell_date: str = Form(...),
    notes: str = Form("")
):
    """固定銘柄分析処理"""
    try:
        # バリデーション
        if not all([model_id.strip(), stock_code.strip(), predicted_price > 0]):
            return templates.TemplateResponse("fixed_stock.html", {
                "request": request,
                "error_message": "必須項目を全て入力してください。"
            })
        
        # 銘柄コードの整形（数字のみ取り出し）
        import re
        stock_code = re.sub(r'[^0-9]', '', stock_code.strip())
        
        if len(stock_code) != 4:
            return templates.TemplateResponse("fixed_stock.html", {
                "request": request,
                "error_message": "銘柄コードは4桁の数字で入力してください。"
            })
        
        buy_date_obj = datetime.strptime(buy_date, "%Y-%m-%d").date()
        sell_date_obj = datetime.strptime(sell_date, "%Y-%m-%d").date()
        
        if buy_date_obj >= sell_date_obj:
            return templates.TemplateResponse("fixed_stock.html", {
                "request": request,
                "error_message": "売却日は購入日より後の日付を選択してください。"
            })
        
        # 銘柄情報を取得して表示
        stock_info = StockAnalyzer.get_stock_info(stock_code)
        print(f"銘柄情報: {stock_info}")
        
        # 株価データ取得
        print(f"購入日の株価取得開始: {stock_code} - {buy_date}")
        buy_price, actual_buy_date = StockAnalyzer.get_closest_business_day_price(
            stock_code, buy_date
        )
        
        if buy_price is None:
            return templates.TemplateResponse("fixed_stock.html", {
                "request": request,
                "error_message": f"銘柄コード {stock_code} の購入日の株価データを取得できませんでした。銘柄コードが正しいか、または購入日が営業日か確認してください。"
            })
        
        print(f"売却日の株価取得開始: {stock_code} - {sell_date}")
        sell_price, actual_sell_date = StockAnalyzer.get_closest_business_day_price(
            stock_code, sell_date
        )
        
        if sell_price is None:
            return templates.TemplateResponse("fixed_stock.html", {
                "request": request,
                "error_message": f"銘柄コード {stock_code} の売却日の株価データを取得できませんでした。銘柄コードが正しいか、または売却日が営業日か確認してください。"
            })
        
        # 計算
        profit_loss = sell_price - buy_price
        return_rate = StockAnalyzer.calculate_return_rate(buy_price, sell_price)
        prediction_accuracy = StockAnalyzer.calculate_prediction_accuracy(
            sell_price, predicted_price
        )
        period_days = (sell_date_obj - buy_date_obj).days
        
        # 結果表示
        result = {
            "model_id": model_id,
            "stock_code": stock_code,
            "stock_name": stock_info.get("name", "不明"),
            "buy_price": buy_price,
            "sell_price": sell_price,
            "predicted_price": predicted_price,
            "profit_loss": profit_loss,
            "return_rate": return_rate,
            "prediction_accuracy": prediction_accuracy,
            "period_days": period_days,
            "actual_buy_date": actual_buy_date,
            "actual_sell_date": actual_sell_date,
            "notes": notes,
            "prediction_error": abs(sell_price - predicted_price)  # 予測誤差を追加
        }
        
        return templates.TemplateResponse("fixed_stock.html", {
            "request": request,
            "result": result
        })
        
    except ValueError as e:
        return templates.TemplateResponse("fixed_stock.html", {
            "request": request,
            "error_message": f"入力値にエラーがあります: {str(e)}"
        })
    except Exception as e:
        print(f"未知のエラー: {str(e)}")
        import traceback
        print(f"詳細エラー: {traceback.format_exc()}")
        return templates.TemplateResponse("fixed_stock.html", {
            "request": request,
            "error_message": f"エラーが発生しました。しばらくしてから再度お試しください。(エラー: {str(e)})"
        })

@app.post("/fixed-stock/save")
async def save_fixed_stock(
    model_id: str = Form(...),
    stock_code: str = Form(...),
    buy_date: str = Form(...),
    buy_price: float = Form(...),
    sell_date: str = Form(...),
    sell_price: float = Form(...),
    predicted_price: float = Form(...),
    profit_loss: float = Form(...),
    return_rate: float = Form(...),
    prediction_accuracy: float = Form(...),
    period_days: int = Form(...),
    notes: str = Form("")
):
    """固定銘柄分析結果を保存"""
    try:
        save_data = {
            "execution_date": datetime.now(),
            "model_id": model_id,
            "stock_code": stock_code,
            "buy_date": buy_date,
            "buy_price": buy_price,
            "sell_date": sell_date,
            "sell_price": sell_price,
            "predicted_price": predicted_price,
            "profit_loss": profit_loss,
            "return_rate": return_rate,
            "prediction_accuracy": prediction_accuracy,
            "period_days": period_days,
            "notes": notes
        }
        
        success = DatabaseManager.save_fixed_stock_analysis(save_data)
        
        if success:
            return RedirectResponse(
                url="/fixed-stock?success=データが正常に保存されました！履歴分析ページで確認できます。",
                status_code=303
            )
        else:
            return RedirectResponse(
                url="/fixed-stock?error=データの保存に失敗しました。",
                status_code=303
            )
    except Exception as e:
        return RedirectResponse(
            url=f"/fixed-stock?error=保存エラー: {str(e)}",
            status_code=303
        )

@app.get("/stock-selection", response_class=HTMLResponse)
async def stock_selection_form(request: Request, success: Optional[str] = None, error: Optional[str] = None):
    """銘柄選定分析フォーム"""
    return templates.TemplateResponse("stock_selection.html", {
        "request": request,
        "success_message": success,
        "error_message": error
    })

@app.post("/stock-selection")
async def stock_selection_submit(
    request: Request,
    analysis_period: str = Form(...),
    model_id: str = Form(...),
    stock_code: str = Form(...),
    selection_reason: str = Form(...),
    buy_date: str = Form(...),
    notes: str = Form("")
):
    """銘柄選定分析処理"""
    try:
        # バリデーション
        if not all([analysis_period.strip(), model_id.strip(), stock_code.strip(), selection_reason.strip()]):
            return templates.TemplateResponse("stock_selection.html", {
                "request": request,
                "error_message": "必須項目を全て入力してください。"
            })
        
        # 銘柄コードの整形（数字のみ取り出し）
        import re
        stock_code = re.sub(r'[^0-9]', '', stock_code.strip())
        
        if len(stock_code) != 4:
            return templates.TemplateResponse("stock_selection.html", {
                "request": request,
                "error_message": "銘柄コードは4桁の数字で入力してください。"
            })
        
        # 売却日を計算
        period_mapping = {"1週間": 7, "1ヶ月": 30, "3ヶ月": 90, "6ヶ月": 180, "1年": 365}
        
        if analysis_period not in period_mapping:
            return templates.TemplateResponse("stock_selection.html", {
                "request": request,
                "error_message": "有効な分析期間を選択してください。"
            })
        
        buy_date_obj = datetime.strptime(buy_date, "%Y-%m-%d").date()
        sell_date_obj = buy_date_obj + timedelta(days=period_mapping[analysis_period])
        
        # 銘柄情報を取得して表示
        stock_info = StockAnalyzer.get_stock_info(stock_code)
        print(f"銘柄情報: {stock_info}")
        
        # 株価データ取得
        print(f"購入日の株価取得開始: {stock_code} - {buy_date}")
        buy_price, actual_buy_date = StockAnalyzer.get_closest_business_day_price(
            stock_code, buy_date
        )
        
        if buy_price is None:
            return templates.TemplateResponse("stock_selection.html", {
                "request": request,
                "error_message": f"銘柄コード {stock_code} の購入日の株価データを取得できませんでした。銘柄コードが正しいか、または購入日が営業日か確認してください。"
            })
        
        print(f"売却日の株価取得開始: {stock_code} - {sell_date_obj.strftime('%Y-%m-%d')}")
        sell_price, actual_sell_date = StockAnalyzer.get_closest_business_day_price(
            stock_code, sell_date_obj.strftime("%Y-%m-%d")
        )
        
        if sell_price is None:
            return templates.TemplateResponse("stock_selection.html", {
                "request": request,
                "error_message": f"銘柄コード {stock_code} の売却日の株価データを取得できませんでした。銘柄コードが正しいか確認してください。"
            })
        
        # 計算
        profit_loss = sell_price - buy_price
        return_rate = StockAnalyzer.calculate_return_rate(buy_price, sell_price)
        actual_period_days = (
            datetime.strptime(actual_sell_date, "%Y-%m-%d").date() -
            datetime.strptime(actual_buy_date, "%Y-%m-%d").date()
        ).days
        
        # 結果表示
        result = {
            "analysis_period": analysis_period,
            "model_id": model_id,
            "stock_code": stock_code,
            "stock_name": stock_info.get("name", "不明"),
            "selection_reason": selection_reason,
            "buy_price": buy_price,
            "sell_price": sell_price,
            "profit_loss": profit_loss,
            "return_rate": return_rate,
            "period_days": actual_period_days,
            "actual_buy_date": actual_buy_date,
            "actual_sell_date": actual_sell_date,
            "notes": notes
        }
        
        return templates.TemplateResponse("stock_selection.html", {
            "request": request,
            "result": result
        })
        
    except ValueError as e:
        return templates.TemplateResponse("stock_selection.html", {
            "request": request,
            "error_message": f"入力値にエラーがあります: {str(e)}"
        })
    except Exception as e:
        print(f"未知のエラー: {str(e)}")
        import traceback
        print(f"詳細エラー: {traceback.format_exc()}")
        return templates.TemplateResponse("stock_selection.html", {
            "request": request,
            "error_message": f"エラーが発生しました。しばらくしてから再度お試しください。(エラー: {str(e)})"
        })

@app.post("/stock-selection/save")
async def save_stock_selection(
    analysis_period: str = Form(...),
    model_id: str = Form(...),
    stock_code: str = Form(...),
    selection_reason: str = Form(...),
    buy_date: str = Form(...),
    buy_price: float = Form(...),
    sell_date: str = Form(...),
    sell_price: float = Form(...),
    profit_loss: float = Form(...),
    return_rate: float = Form(...),
    period_days: int = Form(...),
    notes: str = Form("")
):
    """銘柄選定分析結果を保存"""
    try:
        save_data = {
            "execution_date": datetime.now(),
            "analysis_period": analysis_period,
            "model_id": model_id,
            "stock_code": stock_code,
            "selection_reason": selection_reason,
            "buy_date": buy_date,
            "buy_price": buy_price,
            "sell_date": sell_date,
            "sell_price": sell_price,
            "profit_loss": profit_loss,
            "return_rate": return_rate,
            "period_days": period_days,
            "notes": notes
        }
        
        success = DatabaseManager.save_stock_selection_analysis(save_data)
        
        if success:
            return RedirectResponse(
                url="/stock-selection?success=データが正常に保存されました！履歴分析ページで確認できます。",
                status_code=303
            )
        else:
            return RedirectResponse(
                url="/stock-selection?error=データの保存に失敗しました。",
                status_code=303
            )
    except Exception as e:
        return RedirectResponse(
            url=f"/stock-selection?error=保存エラー: {str(e)}",
            status_code=303
        )

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    """履歴分析ページ"""
    fixed_df = DatabaseManager.load_fixed_stock_data()
    selection_df = DatabaseManager.load_stock_selection_data()
    stats = DatabaseManager.get_summary_stats()
    
    return templates.TemplateResponse("history.html", {
        "request": request,
        "fixed_data": fixed_df.to_dict('records') if not fixed_df.empty else [],
        "selection_data": selection_df.to_dict('records') if not selection_df.empty else [],
        "stats": stats
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
