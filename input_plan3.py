import streamlit as st
from datetime import datetime, time
import pandas as pd
import os

# CSVファイル名
CSV_FILE = "schedules.csv"

# 既存のCSVがなければヘッダー付きで作成
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["内容", "日付", "開始時間", "終了時間", "終日", "反復設定"])
    df_init.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

# タイトル
st.title("📅 予定入力画面")

# 入力欄
title = st.text_input("予定の内容")
date = st.date_input("予定の日付", value=datetime.today())
is_all_day = st.checkbox("終日")

if not is_all_day:
    col1, col2 = st.columns(2)
    with col1:
        start_time = st.time_input("開始時間", value=time(9, 0), key="start")
    with col2:
        end_time = st.time_input("終了時間", value=time(10, 0), key="end")

    if end_time <= start_time:
        st.warning("終了時間は開始時間より後にしてください。")
else:
    start_time = time(0, 0)
    end_time = time(23, 59)

repeat_option = st.selectbox(
    "反復設定",
    ("なし", "1日ごと", "1週間ごと", "2週間ごと", "1カ月ごと")
)

# 保存ボタン
if st.button("予定を追加"):
    if is_all_day or end_time > start_time:
        # 予定データを辞書でまとめる
        schedule_data = {
            "内容": title,
            "日付": date.strftime('%Y-%m-%d'),
            "開始時間": start_time.strftime('%H:%M'),
            "終了時間": end_time.strftime('%H:%M'),
            "終日": "はい" if is_all_day else "いいえ",
            "反復設定": repeat_option
        }

        # CSVに追記
        df = pd.DataFrame([schedule_data])
        df.to_csv(CSV_FILE, mode='a', header=False, index=False, encoding="utf-8-sig")

        st.success("✅ 予定がCSVに保存されました！")
        st.write(schedule_data)
    else:
        st.error("❌ 時間設定が正しくありません。")
