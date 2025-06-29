import streamlit as st
import streamlit_calendar as st_calendar
import os
import sqlite3
from datetime import datetime
# db.pyから必要な関数をインポート
from db import update_schedule_datetime, init_db

# データベースファイルとテーブルがなければ作成
init_db()

DB_NAME = "./schedule_app.db"

def get_events_from_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, start_time, end_time, is_all_day FROM schedules")
    rows = cursor.fetchall()
    conn.close()

    event_list = []
    for row in rows:
        event = {}
        event['id'] = str(row[0]) # IDは文字列型が安全
        event['title'] = row[1]
        start_time_str = row[2]
        end_time_str = row[3]
        is_all_day = row[4]

        if is_all_day:
            event['start'] = start_time_str.split(' ')[0]
            event['end'] = end_time_str.split(' ')[0]
            event['allDay'] = True
        else:
            start_dt = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M')
            end_dt = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M')
            event['start'] = start_dt.isoformat()
            event['end'] = end_dt.isoformat()
            event['allDay'] = False
        
        event['editable'] = True
        event_list.append(event)
    return event_list

event_list = get_events_from_db()

if st.button('予定を追加'):
    st.switch_page('pages/schedule.py')

options = {
    'initialView': 'dayGridMonth',
    'headerToolbar': {
        'left': 'today prev,next',
        'center': 'title',
        'right': 'dayGridMonth,timeGridWeek,timeGridDay',
    },
    'locale': 'ja',
    'editable': True,
    'selectable': True,
    'buttonText': {
        'today': '当日',
        'month': '月ごと',
        'week': '週ごと',
        'day': '日ごと',
    },
}

calendar = st_calendar.calendar(events=event_list, options=options, key="calendar")

# --- ▼▼▼ ここからが頂いた情報に基づく最終修正部分です ▼▼▼ ---

# 1. 'eventDrop' ではなく 'eventChange' をチェックする
if calendar and 'eventChange' in calendar:
    
    # 2. 正しい階層から変更後のイベント情報を取得する
    event_info = calendar['eventChange']['event']
    event_id = event_info['id']

    # 3. タイムゾーン付きのISO形式を直接パースする
    #    '2025-06-30T09:00:00+09:00' のような形式を正しく解釈
    new_start_dt = datetime.fromisoformat(event_info['start'])
    new_end_dt = datetime.fromisoformat(event_info['end'])

    # 4. DB保存形式（'YYYY-MM-DD HH:MM'）に変換
    db_start_str = new_start_dt.strftime('%Y-%m-%d %H:%M')
    db_end_str = new_end_dt.strftime('%Y-%m-%d %H:%M')

    try:
        # データベースを更新
        update_schedule_datetime(
            event_id=event_id,
            new_start=db_start_str,
            new_end=db_end_str
        )
        # 変更を反映させるためにページを再実行
        st.rerun()
    except Exception as e:
        st.error("データベースの更新中にエラーが発生しました。")
        st.error(e)

# --- ▲▲▲ 修正部分はここまで ▲▲▲ ---