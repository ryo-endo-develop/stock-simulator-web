"""
統計分析モジュール
LLMモデルのパフォーマンス分析とランキング機能
"""

from typing import Dict, List, Optional

import pandas as pd

from database import DatabaseManager


class ModelAnalytics:
    """LLMモデルの統計分析クラス"""

    @staticmethod
    def get_model_performance_ranking() -> List[Dict]:
        """モデル別パフォーマンスランキングを取得"""
        try:
            # データを取得
            fixed_df = DatabaseManager.load_fixed_stock_data()
            selection_df = DatabaseManager.load_stock_selection_data()

            # AIモデル情報を取得
            ai_models = DatabaseManager.get_ai_models()
            model_mapping = {
                model["model_code"]: model["display_name"] for model in ai_models
            }

            model_stats = {}

            # 固定銘柄分析データの統計
            if not fixed_df.empty:
                for model_id in fixed_df["model_id"].unique():
                    model_data = fixed_df[fixed_df["model_id"] == model_id]

                    if model_id not in model_stats:
                        model_stats[model_id] = {
                            "model_name": model_mapping.get(model_id, model_id),
                            "fixed_analyses": 0,
                            "selection_analyses": 0,
                            "total_analyses": 0,
                            "fixed_win_rate": 0,
                            "selection_win_rate": 0,
                            "overall_win_rate": 0,
                            "avg_prediction_accuracy": 0,
                            "avg_return_rate": 0,
                            "total_profit_loss": 0,
                            "best_trade_return": 0,
                            "worst_trade_return": 0,
                        }

                    # 固定銘柄分析の統計
                    model_stats[model_id]["fixed_analyses"] = len(model_data)
                    model_stats[model_id]["fixed_win_rate"] = (
                        model_data["return_rate"] > 0
                    ).mean() * 100
                    model_stats[model_id]["avg_prediction_accuracy"] = model_data[
                        "prediction_accuracy"
                    ].mean()

                    # 全体統計に加算
                    fixed_returns = model_data["return_rate"].tolist()
                    fixed_profits = model_data["profit_loss"].sum()

                    model_stats[model_id]["avg_return_rate"] = model_data[
                        "return_rate"
                    ].mean()
                    model_stats[model_id]["total_profit_loss"] += fixed_profits

                    if fixed_returns:
                        model_stats[model_id]["best_trade_return"] = max(
                            model_stats[model_id]["best_trade_return"],
                            max(fixed_returns),
                        )
                        model_stats[model_id]["worst_trade_return"] = min(
                            model_stats[model_id]["worst_trade_return"],
                            min(fixed_returns),
                        )

            # 銘柄選定分析データの統計
            if not selection_df.empty:
                for model_id in selection_df["model_id"].unique():
                    model_data = selection_df[selection_df["model_id"] == model_id]

                    if model_id not in model_stats:
                        model_stats[model_id] = {
                            "model_name": model_mapping.get(model_id, model_id),
                            "fixed_analyses": 0,
                            "selection_analyses": 0,
                            "total_analyses": 0,
                            "fixed_win_rate": 0,
                            "selection_win_rate": 0,
                            "overall_win_rate": 0,
                            "avg_prediction_accuracy": 0,
                            "avg_return_rate": 0,
                            "total_profit_loss": 0,
                            "best_trade_return": 0,
                            "worst_trade_return": 0,
                        }

                    # 銘柄選定分析の統計
                    model_stats[model_id]["selection_analyses"] = len(model_data)
                    model_stats[model_id]["selection_win_rate"] = (
                        model_data["return_rate"] > 0
                    ).mean() * 100

                    # 全体統計に加算（平均を再計算）
                    all_returns = []
                    all_profits = 0

                    # 固定銘柄分析のデータも含める
                    if not fixed_df.empty and model_id in fixed_df["model_id"].values:
                        fixed_model_data = fixed_df[fixed_df["model_id"] == model_id]
                        all_returns.extend(fixed_model_data["return_rate"].tolist())
                        all_profits += fixed_model_data["profit_loss"].sum()

                    # 銘柄選定分析のデータを追加
                    all_returns.extend(model_data["return_rate"].tolist())
                    all_profits += model_data["profit_loss"].sum()

                    if all_returns:
                        model_stats[model_id]["avg_return_rate"] = sum(
                            all_returns
                        ) / len(all_returns)
                        model_stats[model_id]["overall_win_rate"] = (
                            sum(1 for r in all_returns if r > 0)
                            / len(all_returns)
                            * 100
                        )
                        model_stats[model_id]["best_trade_return"] = max(all_returns)
                        model_stats[model_id]["worst_trade_return"] = min(all_returns)

                    model_stats[model_id]["total_profit_loss"] = all_profits

            # 総分析数を計算
            for model_id in model_stats:
                model_stats[model_id]["total_analyses"] = (
                    model_stats[model_id]["fixed_analyses"]
                    + model_stats[model_id]["selection_analyses"]
                )

            # ランキング用のリストに変換
            ranking = []
            for model_id, stats in model_stats.items():
                ranking.append(
                    {
                        "model_id": model_id,
                        "model_name": stats["model_name"],
                        "total_analyses": stats["total_analyses"],
                        "fixed_analyses": stats["fixed_analyses"],
                        "selection_analyses": stats["selection_analyses"],
                        "overall_win_rate": round(stats["overall_win_rate"], 1),
                        "fixed_win_rate": round(stats["fixed_win_rate"], 1),
                        "selection_win_rate": round(stats["selection_win_rate"], 1),
                        "avg_prediction_accuracy": round(
                            stats["avg_prediction_accuracy"], 1
                        ),
                        "avg_return_rate": round(stats["avg_return_rate"], 2),
                        "total_profit_loss": round(stats["total_profit_loss"], 0),
                        "best_trade_return": round(stats["best_trade_return"], 2),
                        "worst_trade_return": round(stats["worst_trade_return"], 2),
                    }
                )

            # 総合勝率でソート（降順）
            ranking.sort(key=lambda x: x["overall_win_rate"], reverse=True)

            return ranking

        except Exception as e:
            print(f"モデルパフォーマンス分析エラー: {str(e)}")
            return []

    @staticmethod
    def get_filtered_data(
        data_type: str = "all",
        model_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        min_return: Optional[float] = None,
        max_return: Optional[float] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Dict:
        """フィルタ条件に基づいてデータを取得"""
        try:
            fixed_df = DatabaseManager.load_fixed_stock_data()
            selection_df = DatabaseManager.load_stock_selection_data()

            # AIモデル情報を取得
            ai_models = DatabaseManager.get_ai_models()
            model_mapping = {
                model["model_code"]: model["display_name"] for model in ai_models
            }

            # フィルタリング処理
            def apply_filters(df):
                if df.empty:
                    return df

                # モデルIDでフィルタリング
                if model_id:
                    df = df[df["model_id"] == model_id]

                # 日付範囲でフィルタリング
                if start_date:
                    start_date_obj = pd.to_datetime(start_date)
                    df = df[pd.to_datetime(df["execution_date"]) >= start_date_obj]

                if end_date:
                    end_date_obj = pd.to_datetime(end_date)
                    df = df[pd.to_datetime(df["execution_date"]) <= end_date_obj]

                # 騰落率範囲でフィルタリング
                if min_return is not None:
                    df = df[df["return_rate"] >= min_return]

                if max_return is not None:
                    df = df[df["return_rate"] <= max_return]

                return df

            # データタイプに応じてフィルタリング
            if data_type == "fixed":
                fixed_df = apply_filters(fixed_df)
                selection_df = pd.DataFrame()
            elif data_type == "selection":
                selection_df = apply_filters(selection_df)
                fixed_df = pd.DataFrame()
            else:  # "all"
                fixed_df = apply_filters(fixed_df)
                selection_df = apply_filters(selection_df)

            # モデル名を追加
            if not fixed_df.empty:
                fixed_df["model_display_name"] = (
                    fixed_df["model_id"].map(model_mapping).fillna(fixed_df["model_id"])
                )
                # ソート処理
                if sort_by in fixed_df.columns:
                    ascending = sort_order == "asc"
                    fixed_df = fixed_df.sort_values(by=sort_by, ascending=ascending)

            if not selection_df.empty:
                selection_df["model_display_name"] = (
                    selection_df["model_id"]
                    .map(model_mapping)
                    .fillna(selection_df["model_id"])
                )
                # ソート処理
                if sort_by in selection_df.columns:
                    ascending = sort_order == "asc"
                    selection_df = selection_df.sort_values(
                        by=sort_by, ascending=ascending
                    )

            return {
                "fixed_data": fixed_df.to_dict("records") if not fixed_df.empty else [],
                "selection_data": selection_df.to_dict("records")
                if not selection_df.empty
                else [],
                "total_records": len(fixed_df) + len(selection_df),
            }

        except Exception as e:
            print(f"フィルタリングエラー: {str(e)}")
            return {"fixed_data": [], "selection_data": [], "total_records": 0}

    @staticmethod
    def get_model_comparison_chart_data() -> Dict:
        """モデル比較チャート用のデータを取得"""
        try:
            ranking = ModelAnalytics.get_model_performance_ranking()

            if not ranking:
                return {"labels": [], "win_rates": [], "accuracies": [], "returns": []}

            # 上位5モデルのみを取得
            top_models = ranking[:5]

            return {
                "labels": [model["model_name"] for model in top_models],
                "win_rates": [model["overall_win_rate"] for model in top_models],
                "accuracies": [
                    model["avg_prediction_accuracy"] for model in top_models
                ],
                "returns": [model["avg_return_rate"] for model in top_models],
            }

        except Exception as e:
            print(f"チャートデータ取得エラー: {str(e)}")
            return {"labels": [], "win_rates": [], "accuracies": [], "returns": []}
