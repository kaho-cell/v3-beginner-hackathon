import streamlit as st
import streamlit_calendar as st_calendar
import csv
import os
import sqlite3
from datetime import datetime

# db.pyから必要な関数をインポート（もしdb.pyが別のファイルであれば）
# from db import DB_NAME # DB_NAMEがdb.pyで定義されている場合
# または直接データベース名を定義
DB_NAME = "./schedule_app.db" #

def get_events_from_db():
    conn = sqlite3.connect(DB_NAME) #
    cursor = conn.cursor()

    # schedulesテーブルからデータを取得
    # 必要な列をここに指定します。CSVの '内容', '日付', '開始時間', '終了時間' に対応するもの
    cursor.execute("SELECT id, title, start_time, end_time, is_all_day FROM schedules") #
    rows = cursor.fetchall() #

    conn.close() #

    event_list = []
    for row in rows:
        event = {}
        # データベースの列名と辞書のキーを対応付け
        event['id'] = row[0]
        event['title'] = row[1]

        start_time_str = row[2] # 例: '2023-10-26 09:00'
        end_time_str = row[3]   # 例: '2023-10-26 10:00'
        is_all_day = row[4]     # BOOLEAN値

        if is_all_day: #
            # 終日イベントの場合、日付のみを'YYYY-MM-DD'形式で取得
            event['start'] = start_time_str.split(' ')[0]
            event['end'] = end_time_str.split(' ')[0]
            event['allDay'] = True
        else:
            # 特定の時間を持つイベントの場合、ISO 8601形式 'YYYY-MM-DDTHH:MM:SS' に変換
            # SQLiteのTEXT型からdatetimeオブジェクトに変換してからISO形式に
            start_dt = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M')
            end_dt = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M')
            event['start'] = start_dt.isoformat()
            event['end'] = end_dt.isoformat()
            event['allDay'] = False

        event['editable'] = True # 必要に応じて設定
        event_list.append(event)

    return event_list

# 関数を呼び出してイベントリストを取得
event_list = get_events_from_db()

if st.button('予定を追加'):
    st.switch_page('pages/schedule.py')

# event_list = []

# file_path = './st_calendar/schedules.csv'

# if os.path.exists(file_path):
#     with open(file_path, encoding='utf-8') as f:
#         reader = csv.DictReader(f)
#         if reader.fieldnames:
#             fieldnames = [field.lstrip('\ufeff') for field in reader.fieldnames]
#             reader.fieldnames = fieldnames
#         l = [row for row in reader]
#         i = 0
#         for e in l:
#             event = {}
#             event['id'] = i
#             event['title'] = e['内容']
#             event['start'] = e['日付'] + 'T' + e['開始時間']
#             event['end'] = e['日付'] + 'T' + e['終了時間']
#             event['editable'] = True
#             event_list.append(event)
#             i += 1

options = {
    'initialView': 'dayGridMonth',
    # left/center/rightの3つの領域に表示するものはこの例の順番でなくてもいい
    'headerToolbar': {
        # ヘッダーの左側に表示するものを指定
        # 日付を移動するボタンが表示される。'today'を省略してもいい
        'left': 'today prev,next',
        # ヘッダーの中央に表示するものを指定
        # 'title'は表示されている日付などのこと
        'center': 'title',
        # ヘッダーの右側に表示するものを指定
        # ビュー名をカンマ区切りで列挙して指定するとビューを切り替えるためのボタンが表示される
        'right': 'dayGridMonth,timeGridWeek,timeGridDay',
    },
    'footerToolbar': {
        # ヘッダーと同じものをフッターにも配置できる。配置しない場合は省力する
        # 'center': 'title',
    },
    'titleFormat': {
        # 例えば月の表記を数字を指定できる
        # 年/月/日の順番にするのはlocaleで設定
        'year': 'numeric', 'month': '2-digit', 'day': '2-digit'
    },
    'buttonText': {
        # 各ボタンを日本語化してみる
        'today': '当日',
        'month': '月ごと',
        'week': '週ごと',
        'day': '日ごと',
        'list': 'リスト'
    },
    'locale': 'ja', # 日本語化する
    'firstDay': '1', # 週の最初を月曜日(1)にする。デフォルトは日曜日(0)
}

calendar = st_calendar.calendar(events = event_list, options = options)
# st.write(calendar)