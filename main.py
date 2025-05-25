import io
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from analytics import ModelAnalytics
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
    return templates.TemplateResponse(
        "index.html", {"request": request, "stats": stats}
    )


@app.get("/fixed-stock", response_class=HTMLResponse)
async def fixed_stock_form(
    request: Request, success: Optional[str] = None, error: Optional[str] = None
):
    """固定銘柄分析フォーム"""
    ai_models = DatabaseManager.get_ai_models()
    return templates.TemplateResponse(
        "fixed_stock.html",
        {
            "request": request,
            "success_message": success,
            "error_message": error,
            "ai_models": ai_models,
        },
    )


@app.post("/fixed-stock")
async def fixed_stock_submit(
    request: Request,
    model_id: str = Form(...),
    stock_code: str = Form(...),
    predicted_price: float = Form(...),
    buy_date: str = Form(...),
    sell_date: str = Form(...),
    notes: str = Form(""),
):
    """固定銘柄分析処理"""
    try:
        # バリデーション
        if not all([model_id.strip(), stock_code.strip(), predicted_price > 0]):
            return templates.TemplateResponse(
                "fixed_stock.html",
                {
                    "request": request,
                    "error_message": "必須項目を全て入力してください。",
                },
            )

        # 銘柄コードの整形（数字のみ取り出し）
        import re

        stock_code = re.sub(r"[^0-9]", "", stock_code.strip())

        if len(stock_code) != 4:
            return templates.TemplateResponse(
                "fixed_stock.html",
                {
                    "request": request,
                    "error_message": "銘柄コードは4桁の数字で入力してください。",
                },
            )

        buy_date_obj = datetime.strptime(buy_date, "%Y-%m-%d").date()
        sell_date_obj = datetime.strptime(sell_date, "%Y-%m-%d").date()

        if buy_date_obj >= sell_date_obj:
            return templates.TemplateResponse(
                "fixed_stock.html",
                {
                    "request": request,
                    "error_message": "売却日は購入日より後の日付を選択してください。",
                },
            )

        # 銘柄情報を取得して表示
        stock_info = StockAnalyzer.get_stock_info(stock_code)
        print(f"銘柄情報: {stock_info}")

        # 株価データ取得
        print(f"購入日の株価取得開始: {stock_code} - {buy_date}")
        buy_price, actual_buy_date = StockAnalyzer.get_closest_business_day_price(
            stock_code, buy_date
        )

        if buy_price is None:
            return templates.TemplateResponse(
                "fixed_stock.html",
                {
                    "request": request,
                    "error_message": f"銘柄コード {stock_code} の購入日の株価データを取得できませんでした。銘柄コードが正しいか、または購入日が営業日か確認してください。",
                },
            )

        print(f"売却日の株価取得開始: {stock_code} - {sell_date}")
        sell_price, actual_sell_date = StockAnalyzer.get_closest_business_day_price(
            stock_code, sell_date
        )

        if sell_price is None:
            return templates.TemplateResponse(
                "fixed_stock.html",
                {
                    "request": request,
                    "error_message": f"銘柄コード {stock_code} の売却日の株価データを取得できませんでした。銘柄コードが正しいか、または売却日が営業日か確認してください。",
                },
            )

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
            "prediction_error": abs(sell_price - predicted_price),  # 予測誤差を追加
        }

        return templates.TemplateResponse(
            "fixed_stock.html", {"request": request, "result": result}
        )

    except ValueError as e:
        return templates.TemplateResponse(
            "fixed_stock.html",
            {
                "request": request,
                "error_message": f"入力値にエラーがあります: {str(e)}",
            },
        )
    except Exception as e:
        print(f"未知のエラー: {str(e)}")
        import traceback

        print(f"詳細エラー: {traceback.format_exc()}")
        return templates.TemplateResponse(
            "fixed_stock.html",
            {
                "request": request,
                "error_message": f"エラーが発生しました。しばらくしてから再度お試しください。(エラー: {str(e)})",
            },
        )


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
    notes: str = Form(""),
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
            "notes": notes,
        }

        success = DatabaseManager.save_fixed_stock_analysis(save_data)

        if success:
            return RedirectResponse(
                url="/fixed-stock?success=データが正常に保存されました！履歴分析ページで確認できます。",
                status_code=303,
            )
        else:
            return RedirectResponse(
                url="/fixed-stock?error=データの保存に失敗しました。", status_code=303
            )
    except Exception as e:
        return RedirectResponse(
            url=f"/fixed-stock?error=保存エラー: {str(e)}", status_code=303
        )


@app.get("/stock-selection", response_class=HTMLResponse)
async def stock_selection_form(
    request: Request, success: Optional[str] = None, error: Optional[str] = None
):
    """銘柄選定分析フォーム"""
    ai_models = DatabaseManager.get_ai_models()
    return templates.TemplateResponse(
        "stock_selection.html",
        {
            "request": request,
            "success_message": success,
            "error_message": error,
            "ai_models": ai_models,
        },
    )


@app.post("/stock-selection")
async def stock_selection_submit(
    request: Request,
    analysis_period: str = Form(...),
    model_id: str = Form(...),
    stock_code: str = Form(...),
    selection_reason: str = Form(...),
    buy_date: str = Form(...),
    notes: str = Form(""),
):
    """銘柄選定分析処理"""
    try:
        # バリデーション
        if not all(
            [
                analysis_period.strip(),
                model_id.strip(),
                stock_code.strip(),
                selection_reason.strip(),
            ]
        ):
            return templates.TemplateResponse(
                "stock_selection.html",
                {
                    "request": request,
                    "error_message": "必須項目を全て入力してください。",
                },
            )

        # 銘柄コードの整形（数字のみ取り出し）
        import re

        stock_code = re.sub(r"[^0-9]", "", stock_code.strip())

        if len(stock_code) != 4:
            return templates.TemplateResponse(
                "stock_selection.html",
                {
                    "request": request,
                    "error_message": "銘柄コードは4桁の数字で入力してください。",
                },
            )

        # 売却日を計算
        period_mapping = {
            "1週間": 7,
            "1ヶ月": 30,
            "3ヶ月": 90,
            "6ヶ月": 180,
            "1年": 365,
        }

        if analysis_period not in period_mapping:
            return templates.TemplateResponse(
                "stock_selection.html",
                {
                    "request": request,
                    "error_message": "有効な分析期間を選択してください。",
                },
            )

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
            return templates.TemplateResponse(
                "stock_selection.html",
                {
                    "request": request,
                    "error_message": f"銘柄コード {stock_code} の購入日の株価データを取得できませんでした。銘柄コードが正しいか、または購入日が営業日か確認してください。",
                },
            )

        print(
            f"売却日の株価取得開始: {stock_code} - {sell_date_obj.strftime('%Y-%m-%d')}"
        )
        sell_price, actual_sell_date = StockAnalyzer.get_closest_business_day_price(
            stock_code, sell_date_obj.strftime("%Y-%m-%d")
        )

        if sell_price is None:
            return templates.TemplateResponse(
                "stock_selection.html",
                {
                    "request": request,
                    "error_message": f"銘柄コード {stock_code} の売却日の株価データを取得できませんでした。銘柄コードが正しいか確認してください。",
                },
            )

        # 計算
        profit_loss = sell_price - buy_price
        return_rate = StockAnalyzer.calculate_return_rate(buy_price, sell_price)
        actual_period_days = (
            datetime.strptime(actual_sell_date, "%Y-%m-%d").date()
            - datetime.strptime(actual_buy_date, "%Y-%m-%d").date()
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
            "notes": notes,
        }

        return templates.TemplateResponse(
            "stock_selection.html", {"request": request, "result": result}
        )

    except ValueError as e:
        return templates.TemplateResponse(
            "stock_selection.html",
            {
                "request": request,
                "error_message": f"入力値にエラーがあります: {str(e)}",
            },
        )
    except Exception as e:
        print(f"未知のエラー: {str(e)}")
        import traceback

        print(f"詳細エラー: {traceback.format_exc()}")
        return templates.TemplateResponse(
            "stock_selection.html",
            {
                "request": request,
                "error_message": f"エラーが発生しました。しばらくしてから再度お試しください。(エラー: {str(e)})",
            },
        )


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
    notes: str = Form(""),
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
            "notes": notes,
        }

        success = DatabaseManager.save_stock_selection_analysis(save_data)

        if success:
            return RedirectResponse(
                url="/stock-selection?success=データが正常に保存されました！履歴分析ページで確認できます。",
                status_code=303,
            )
        else:
            return RedirectResponse(
                url="/stock-selection?error=データの保存に失敗しました。",
                status_code=303,
            )
    except Exception as e:
        return RedirectResponse(
            url=f"/stock-selection?error=保存エラー: {str(e)}", status_code=303
        )


@app.get("/history", response_class=HTMLResponse)
async def history(
    request: Request,
    data_type: Optional[str] = "all",
    model_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_return: Optional[str] = None,
    max_return: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
):
    """履歴分析ページ"""

    # 文字列パラメータを適切な型に変換
    def safe_float_convert(value: Optional[str]) -> Optional[float]:
        if value is None or value.strip() == "":
            return None
        try:
            return float(value)
        except ValueError:
            return None

    min_return_float = safe_float_convert(min_return)
    max_return_float = safe_float_convert(max_return)

    # 空文字列をNoneに変換
    model_id = model_id if model_id and model_id.strip() else None
    start_date = start_date if start_date and start_date.strip() else None
    end_date = end_date if end_date and end_date.strip() else None

    # フィルタリングされたデータを取得
    filtered_data = ModelAnalytics.get_filtered_data(
        data_type=data_type,
        model_id=model_id,
        start_date=start_date,
        end_date=end_date,
        min_return=min_return_float,
        max_return=max_return_float,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    # モデルパフォーマンスランキングを取得
    model_ranking = ModelAnalytics.get_model_performance_ranking()

    # チャート用データを取得
    chart_data = ModelAnalytics.get_model_comparison_chart_data()

    # 統計情報を取得
    stats = DatabaseManager.get_summary_stats()

    # AIモデル一覧を取得（フィルタ用）
    ai_models = DatabaseManager.get_ai_models()

    # フィルタ条件を保持
    filters = {
        "data_type": data_type,
        "model_id": model_id,
        "start_date": start_date,
        "end_date": end_date,
        "min_return": min_return,
        "max_return": max_return,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }

    return templates.TemplateResponse(
        "history.html",
        {
            "request": request,
            "fixed_data": filtered_data["fixed_data"],
            "selection_data": filtered_data["selection_data"],
            "total_filtered_records": filtered_data["total_records"],
            "model_ranking": model_ranking,
            "chart_data": chart_data,
            "stats": stats,
            "ai_models": ai_models,
            "filters": filters,
        },
    )


@app.get("/export/fixed-stock")
async def export_fixed_stock(
    model_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_return: Optional[str] = None,
    max_return: Optional[str] = None,
):
    """固定銘柄分析データをCSVエクスポート"""
    try:
        # 文字列パラメータを適切な型に変換
        def safe_float_convert(value: Optional[str]) -> Optional[float]:
            if value is None or value.strip() == "":
                return None
            try:
                return float(value)
            except ValueError:
                return None

        min_return_float = safe_float_convert(min_return)
        max_return_float = safe_float_convert(max_return)

        # データを取得
        fixed_df = DatabaseManager.load_fixed_stock_data()

        # フィルタリング処理
        if not fixed_df.empty:
            # モデルIDでフィルタリング
            if model_id:
                fixed_df = fixed_df[fixed_df["model_id"] == model_id]

            # 日付範囲でフィルタリング
            if start_date:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                fixed_df = fixed_df[
                    pd.to_datetime(fixed_df["execution_date"]) >= start_date_obj
                ]

            if end_date:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                fixed_df = fixed_df[
                    pd.to_datetime(fixed_df["execution_date"]) <= end_date_obj
                ]

            # 騰落率範囲でフィルタリング
            if min_return_float is not None:
                fixed_df = fixed_df[fixed_df["return_rate"] >= min_return_float]

            if max_return_float is not None:
                fixed_df = fixed_df[fixed_df["return_rate"] <= max_return_float]

        if fixed_df.empty:
            # 空の場合はヘッダーのみのCSVを返す
            headers = [
                "ID",
                "実行日",
                "LLMモデル",
                "銘柄コード",
                "購入日",
                "購入価格",
                "売却日",
                "売却価格",
                "予測価格",
                "损益",
                "騰落率(%)",
                "予測精度(%)",
                "保有期間(日)",
                "備考",
                "作成日時",
            ]
            empty_df = pd.DataFrame(columns=headers)
            csv_content = empty_df.to_csv(index=False, encoding="utf-8-sig")
        else:
            # AIモデル情報を結合
            ai_models = DatabaseManager.get_ai_models()
            model_mapping = {
                model["model_code"]: model["display_name"] for model in ai_models
            }

            # データを整形
            export_df = fixed_df.copy()
            export_df["model_display_name"] = (
                export_df["model_id"].map(model_mapping).fillna(export_df["model_id"])
            )

            # 列名を日本語に変更
            column_mapping = {
                "id": "ID",
                "execution_date": "実行日",
                "model_display_name": "LLMモデル",
                "stock_code": "銘柄コード",
                "buy_date": "購入日",
                "buy_price": "購入価格",
                "sell_date": "売却日",
                "sell_price": "売却価格",
                "predicted_price": "予測価格",
                "profit_loss": "损益",
                "return_rate": "騰落率(%)",
                "prediction_accuracy": "予測精度(%)",
                "period_days": "保有期間(日)",
                "notes": "備考",
                "created_at": "作成日時",
            }

            # 必要な列を選択して並び替え
            columns_to_export = [
                "id",
                "execution_date",
                "model_display_name",
                "stock_code",
                "buy_date",
                "buy_price",
                "sell_date",
                "sell_price",
                "predicted_price",
                "profit_loss",
                "return_rate",
                "prediction_accuracy",
                "period_days",
                "notes",
                "created_at",
            ]

            export_df = export_df[columns_to_export].rename(columns=column_mapping)

            # CSVとしてエクスポート
            csv_content = export_df.to_csv(index=False, encoding="utf-8-sig")

        # ファイル名を生成（日時付き）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fixed_stock_analysis_{timestamp}.csv"

        # CSVファイルとしてダウンロードさせる
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        print(f"エクスポートエラー: {str(e)}")
        return HTMLResponse(
            content=f"<h1>エクスポートエラー</h1><p>{str(e)}</p>", status_code=500
        )


@app.get("/export/stock-selection")
async def export_stock_selection(
    model_id: Optional[str] = None,
    analysis_period: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_return: Optional[str] = None,
    max_return: Optional[str] = None,
):
    """銘柄選定分析データをCSVエクスポート"""
    try:
        # 文字列パラメータを適切な型に変換
        def safe_float_convert(value: Optional[str]) -> Optional[float]:
            if value is None or value.strip() == "":
                return None
            try:
                return float(value)
            except ValueError:
                return None

        min_return_float = safe_float_convert(min_return)
        max_return_float = safe_float_convert(max_return)

        # データを取得
        selection_df = DatabaseManager.load_stock_selection_data()

        # フィルタリング処理
        if not selection_df.empty:
            # モデルIDでフィルタリング
            if model_id:
                selection_df = selection_df[selection_df["model_id"] == model_id]

            # 分析期間でフィルタリング
            if analysis_period:
                selection_df = selection_df[
                    selection_df["analysis_period"] == analysis_period
                ]

            # 日付範囲でフィルタリング
            if start_date:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                selection_df = selection_df[
                    pd.to_datetime(selection_df["execution_date"]) >= start_date_obj
                ]

            if end_date:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                selection_df = selection_df[
                    pd.to_datetime(selection_df["execution_date"]) <= end_date_obj
                ]

            # 騰落率範囲でフィルタリング
            if min_return_float is not None:
                selection_df = selection_df[
                    selection_df["return_rate"] >= min_return_float
                ]

            if max_return_float is not None:
                selection_df = selection_df[
                    selection_df["return_rate"] <= max_return_float
                ]

        if selection_df.empty:
            # 空の場合はヘッダーのみのCSVを返す
            headers = [
                "ID",
                "実行日",
                "分析期間",
                "LLMモデル",
                "銘柄コード",
                "選定理由",
                "購入日",
                "購入価格",
                "売却日",
                "売却価格",
                "损益",
                "騰落率(%)",
                "保有期間(日)",
                "備考",
                "作成日時",
            ]
            empty_df = pd.DataFrame(columns=headers)
            csv_content = empty_df.to_csv(index=False, encoding="utf-8-sig")
        else:
            # AIモデル情報を結合
            ai_models = DatabaseManager.get_ai_models()
            model_mapping = {
                model["model_code"]: model["display_name"] for model in ai_models
            }

            # データを整形
            export_df = selection_df.copy()
            export_df["model_display_name"] = (
                export_df["model_id"].map(model_mapping).fillna(export_df["model_id"])
            )

            # 列名を日本語に変更
            column_mapping = {
                "id": "ID",
                "execution_date": "実行日",
                "analysis_period": "分析期間",
                "model_display_name": "LLMモデル",
                "stock_code": "銘柄コード",
                "selection_reason": "選定理由",
                "buy_date": "購入日",
                "buy_price": "購入価格",
                "sell_date": "売却日",
                "sell_price": "売却価格",
                "profit_loss": "损益",
                "return_rate": "騰落率(%)",
                "period_days": "保有期間(日)",
                "notes": "備考",
                "created_at": "作成日時",
            }

            # 必要な列を選択して並び替え
            columns_to_export = [
                "id",
                "execution_date",
                "analysis_period",
                "model_display_name",
                "stock_code",
                "selection_reason",
                "buy_date",
                "buy_price",
                "sell_date",
                "sell_price",
                "profit_loss",
                "return_rate",
                "period_days",
                "notes",
                "created_at",
            ]

            export_df = export_df[columns_to_export].rename(columns=column_mapping)

            # CSVとしてエクスポート
            csv_content = export_df.to_csv(index=False, encoding="utf-8-sig")

        # ファイル名を生成（日時付き）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stock_selection_analysis_{timestamp}.csv"

        # CSVファイルとしてダウンロードさせる
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        print(f"エクスポートエラー: {str(e)}")
        return HTMLResponse(
            content=f"<h1>エクスポートエラー</h1><p>{str(e)}</p>", status_code=500
        )


@app.get("/export/all")
async def export_all_data():
    """全データを統合してCSVエクスポート"""
    try:
        # 両方のデータを取得
        fixed_df = DatabaseManager.load_fixed_stock_data()
        selection_df = DatabaseManager.load_stock_selection_data()

        # AIモデル情報を取得
        ai_models = DatabaseManager.get_ai_models()
        model_mapping = {
            model["model_code"]: model["display_name"] for model in ai_models
        }

        combined_data = []

        # 固定銘柄分析データを追加
        if not fixed_df.empty:
            for _, row in fixed_df.iterrows():
                combined_data.append(
                    {
                        "ID": row["id"],
                        "分析タイプ": "固定銘柄分析",
                        "実行日": row["execution_date"],
                        "LLMモデル": model_mapping.get(
                            row["model_id"], row["model_id"]
                        ),
                        "銘柄コード": row["stock_code"],
                        "購入日": row["buy_date"],
                        "購入価格": row["buy_price"],
                        "売却日": row["sell_date"],
                        "売却価格": row["sell_price"],
                        "予測価格": row.get("predicted_price", ""),
                        "损益": row["profit_loss"],
                        "騰落率(%)": row["return_rate"],
                        "予測精度(%)": row.get("prediction_accuracy", ""),
                        "分析期間": "",
                        "選定理由": "",
                        "保有期間(日)": row["period_days"],
                        "備考": row.get("notes", ""),
                        "作成日時": row["created_at"],
                    }
                )

        # 銘柄選定分析データを追加
        if not selection_df.empty:
            for _, row in selection_df.iterrows():
                combined_data.append(
                    {
                        "ID": row["id"],
                        "分析タイプ": "銘柄選定分析",
                        "実行日": row["execution_date"],
                        "LLMモデル": model_mapping.get(
                            row["model_id"], row["model_id"]
                        ),
                        "銘柄コード": row["stock_code"],
                        "購入日": row["buy_date"],
                        "購入価格": row["buy_price"],
                        "売却日": row["sell_date"],
                        "売却価格": row["sell_price"],
                        "予測価格": "",
                        "损益": row["profit_loss"],
                        "騰落率(%)": row["return_rate"],
                        "予測精度(%)": "",
                        "分析期間": row["analysis_period"],
                        "選定理由": row["selection_reason"],
                        "保有期間(日)": row["period_days"],
                        "備考": row.get("notes", ""),
                        "作成日時": row["created_at"],
                    }
                )

        # DataFrameとして結合
        if combined_data:
            combined_df = pd.DataFrame(combined_data)
            # 作成日時でソート（新しい順）
            combined_df = combined_df.sort_values("作成日時", ascending=False)
        else:
            # データがない場合は空のDataFrame
            columns = [
                "ID",
                "分析タイプ",
                "実行日",
                "LLMモデル",
                "銘柄コード",
                "購入日",
                "購入価格",
                "売却日",
                "売却価格",
                "予測価格",
                "损益",
                "騰落率(%)",
                "予測精度(%)",
                "分析期間",
                "選定理由",
                "保有期間(日)",
                "備考",
                "作成日時",
            ]
            combined_df = pd.DataFrame(columns=columns)

        # CSVとしてエクスポート
        csv_content = combined_df.to_csv(index=False, encoding="utf-8-sig")

        # ファイル名を生成（日時付き）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"all_analysis_data_{timestamp}.csv"

        # CSVファイルとしてダウンロードさせる
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        print(f"エクスポートエラー: {str(e)}")
        return HTMLResponse(
            content=f"<h1>エクスポートエラー</h1><p>{str(e)}</p>", status_code=500
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
