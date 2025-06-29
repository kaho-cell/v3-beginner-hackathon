import streamlit as st
import streamlit_calendar as st_calendar
import os
import sqlite3
from datetime import datetime
import google.generativeai as genai

DB_NAME = "./schedule_app.db" 

GEMINI_API_KEY = "AIzaSyATIO0rm9jPl_ejrxKPuIsSza3rQL6okkw" 

# 正しい引数名 'api_key' を使用してGemini APIを設定
if not GEMINI_API_KEY:
    st.error("Gemini APIキーが設定されていません。Gemini APIを使用できません。")
    st.stop()
genai.configure(api_key=GEMINI_API_KEY)

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

def generate_schedule_advice(events: list) -> str:
    """
    与えられたイベントリストに基づいて、Gemini APIを使ってスケジュールのアドバイスを生成します。

    Args:
        events (list): データベースから取得したイベントのリスト。

    Returns:
        str: Geminiによって生成されたアドバイス。イベントがない場合はその旨を伝えるメッセージ。
    """
    if not events:
        return "現在、予定が登録されていません。新しい予定を追加してみましょう！"

    # イベント情報をGeminiに渡しやすいテキスト形式に整形
    event_descriptions = []
    for event in events:
        title = event.get('title', '不明なイベント')
        start = event.get('start', '不明な開始時間')
        end = event.get('end', '不明な終了時間')
        all_day = event.get('allDay', False)

        if all_day:
            event_descriptions.append(f"・終日イベント: **{title}** ({start})")
        else:
            event_descriptions.append(f"・イベント: **{title}** ({start} から {end} まで)")

    # プロンプトを作成
    prompt = f"""
    以下の予定とタスクのリストに基づいて、効果的な時間管理、生産性向上、またはストレス軽減のための具体的なアドバイスを生成してください。
    予定が重複している場合や、連続するイベントが多い場合など、特定の状況に合わせたアドバイスも歓迎します。

    アドバイスは箇条書きや短い段落で、分かりやすく具体的に記述してください。

    **現在の予定:**
    {chr(10).join(event_descriptions)}

    **アドバイス:**
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"アドバイスの生成中にエラーが発生しました: {e}"

def delete_event_from_db(event_id):
    """指定されたIDのイベントをデータベースから削除する"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM schedules WHERE id = ?", (event_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        st.error(f"データベースエラー: {e}")
        return False

# 関数を呼び出してイベントリストを取得
if os.path.exists(DB_NAME):
    event_list = get_events_from_db()
# データベースがない場合は空のリスト
else:
    event_list = []

st.header('カレンダー')

# 遷移ボタン
col1, col2 = st.columns(2)
with col1:
    if st.button('予定を追加'):
        st.switch_page('pages/schedule.py')
with col2:
    if st.button('やりたいことリスト'):
        st.switch_page('pages/wantto.py')

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
        # 各ボタンを日本語化
        'today': '当日',
        'month': '月ごと',
        'week': '週ごと',
        'day': '日ごと',
        'list': 'リスト'
    },
    'locale': 'ja', # 日本語化する
    'firstDay': '0', # 週の最初を日曜日(0)にする
    'navLinks': True,
    'selectable': True,
    'editable': True,
}

calendar = st_calendar.calendar(events = event_list, options = options)

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


if calendar and 'eventClick' in calendar:
    clicked_event_info = calendar['eventClick']['event']
    event_id = int(clicked_event_info['id'])
    event_title = clicked_event_info['title']
    
    # 終日イベントかどうかで日付のフォーマットを調整
    if clicked_event_info['allDay']:
        start_date = datetime.fromisoformat(clicked_event_info['start'].split('T')[0]).strftime('%Y年%m月%d日')
        # 終日イベントの場合、endは次の日になることがあるためstartと同じ日付を表示
        end_date = start_date
        time_str = "終日"
    else:
        # FullCalendarからの戻り値はISO形式 (YYYY-MM-DDTHH:MM:SS)
        start_dt = datetime.fromisoformat(clicked_event_info['start'])
        end_dt = datetime.fromisoformat(clicked_event_info['end'])
        start_date = start_dt.strftime('%Y年%m月%d日')
        end_date = end_dt.strftime('%Y年%m月%d日')
        time_str = f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"

    # st.expanderを使って詳細情報を表示
    with st.expander(f"【予定詳細】 {event_title}", expanded=True):
        st.write(f"**日時:** {start_date} {time_str}")
        
        # 削除ボタン
        # keyをユニークにすることで、ボタンが正しく機能するようにする
        if st.button("この予定を削除する", key=f"delete_{event_id}"):
            if delete_event_from_db(event_id):
                st.success(f"予定「{event_title}」を削除しました。")
                # 画面を再読み込みしてカレンダーを更新
                st.rerun() 
            else:
                st.error("予定の削除に失敗しました。")