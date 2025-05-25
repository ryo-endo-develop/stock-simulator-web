#!/usr/bin/env python3
"""
週次株価予測プロンプト生成ツール

使用方法:
    python generate_weekly_prompt.py

機能:
    - 現在日時と来週の日付を自動計算
    - プロンプトテンプレートに日付を埋め込み
    - 実行可能なプロンプトを生成
"""

import os
from datetime import datetime, timedelta


def get_next_monday_friday():
    """来週の月曜日と金曜日の日付を取得"""
    today = datetime.now()

    # 今日が何曜日か取得（月曜日=0, 日曜日=6）
    weekday = today.weekday()

    # 来週の月曜日を計算
    days_until_next_monday = 7 - weekday
    if weekday == 6:  # 日曜日の場合は明日が月曜日
        days_until_next_monday = 1

    next_monday = today + timedelta(days=days_until_next_monday)
    next_friday = next_monday + timedelta(days=4)

    return next_monday, next_friday


def generate_weekly_prompt():
    """週次株価予測プロンプトを生成"""

    # 日付計算
    current_date = datetime.now().strftime("%Y年%m月%d日")
    next_monday, next_friday = get_next_monday_friday()
    next_week_start = next_monday.strftime("%Y年%m月%d日(%a)")
    next_week_end = next_friday.strftime("%Y年%m月%d日(%a)")

    # テンプレートファイルを読み込み
    template_path = os.path.join(
        os.path.dirname(__file__), "weekly_stock_prediction_v2.md"
    )

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # 日付を埋め込み
    prompt = template.format(
        current_date=current_date,
        next_week_start=next_week_start,
        next_week_end=next_week_end,
    )

    # 出力ファイル名を生成
    output_filename = f"weekly_prompt_{datetime.now().strftime('%Y%m%d')}.md"
    output_path = os.path.join(os.path.dirname(__file__), "generated", output_filename)

    # generatedディレクトリがなければ作成
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # プロンプトを保存
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"✅ 週次株価予測プロンプトを生成しました: {output_path}")
    print(f"📅 分析対象期間: {next_week_start} 〜 {next_week_end}")

    return output_path, prompt


def display_prompt_summary():
    """プロンプトの概要を表示"""
    print("\n" + "=" * 60)
    print("📈 週次株価予測プロンプト - 生成完了")
    print("=" * 60)
    print()
    print("🎯 このプロンプトで分析できること:")
    print("   1. 来週1週間で上昇期待の日本株トップ5銘柄")
    print("   2. トヨタ自動車(7203)の詳細な週間値動き予測")
    print()
    print("📊 各銘柄について取得できる情報:")
    print("   ・選定理由（テクニカル・ファンダメンタル分析）")
    print("   ・重視した情報源と分析アプローチ")
    print("   ・リスク要因の詳細分析")
    print("   ・具体的な売買戦略と期待リターン")
    print()
    print("🚗 トヨタ株について:")
    print("   ・予想価格レンジ（最高値・最安値・終値）")
    print("   ・3つのシナリオ分析（強気・中立・弱気）")
    print("   ・テクニカル・ファンダメンタル注目ポイント")
    print("   ・売買判断とリスク管理")
    print()
    print("💡 使用方法:")
    print("   1. 生成されたプロンプトをClaude/ChatGPT等にコピー")
    print("   2. 回答を当システムの銘柄選定分析に入力")
    print("   3. バックテスト結果で予測精度を検証")
    print()
    print("=" * 60)


if __name__ == "__main__":
    try:
        output_path, prompt = generate_weekly_prompt()
        display_prompt_summary()

        # プロンプトの一部をプレビュー表示
        print("\n📋 生成されたプロンプト（プレビュー）:")
        print("-" * 40)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("-" * 40)

    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        import traceback

        traceback.print_exc()
