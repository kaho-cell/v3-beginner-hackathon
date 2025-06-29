import streamlit as st
import streamlit_calendar as st_calendar
import csv
import os



event_list = []
# json_file = open('events.json', 'r')
# event = json.load(json_file)

# for e in event:
#     event_list.append(e)

file_path = './st_calendar/schedules.csv'

if os.path.exists(file_path):
    with open(file_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames:
            fieldnames = [field.lstrip('\ufeff') for field in reader.fieldnames]
            reader.fieldnames = fieldnames
        l = [row for row in reader]
        i = 0
        for e in l:
            event = {}
            event['id'] = i
            event['title'] = e['内容']
            event['start'] = e['日付'] + 'T' + e['開始時間']
            event['end'] = e['日付'] + 'T' + e['終了時間']
            event['editable'] = True
            event_list.append(event)
            i += 1

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
        'right': 'dayGridMonth,timeGridWeek,listWeek',
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
# calendar = st_calendar.calendar(options = options)
st.write(calendar)