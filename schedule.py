import streamlit as st
from datetime import datetime, time
from db import init_db, add_schedule

# 初期化（必要に応じて）
init_db()

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
    "反復設定（※未実装）",
    ("なし", "1日ごと", "1週間ごと", "2週間ごと", "1カ月ごと")
)

# 保存ボタン
if st.button("予定を追加"):
    if is_all_day or end_time > start_time:
        add_schedule(
            title=title,
            date=date.strftime('%Y-%m-%d'),
            start_time=start_time.strftime('%H:%M'),
            end_time=end_time.strftime('%H:%M'),
            is_all_day=is_all_day
        )
        st.success("✅ データベースに予定が保存されました！")
        st.write({
            "内容": title,
            "日付": date.strftime('%Y-%m-%d'),
            "開始時間": start_time.strftime('%H:%M'),
            "終了時間": end_time.strftime('%H:%M'),
            "終日": "はい" if is_all_day else "いいえ",
            "反復設定": repeat_option
        })
    else:
        st.error("❌ 時間設定が正しくありません。")
