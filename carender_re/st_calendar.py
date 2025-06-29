import streamlit as st
import streamlit_calendar as st_calendar
import os
import sqlite3
from datetime import datetime
import google.generativeai as genai

DB_NAME = "./schedule_app.db"

# --- Gemini APIの設定 ---
# 環境変数からAPIキーを読み込むことを推奨します。
# 例: gemini_api_key = os.environ.get("GOOGLE_API_KEY")
# 本番環境ではst.secrets["GOOGLE_API_KEY"]を使用するなど、より安全な方法を選択してください。
# ここでは提示されたAPIキーを直接使用しますが、これは開発・テスト用途に限定してください。
GEMINI_API_KEY = "AIzaSyATIO0rm9jPl_ejrxKPuIsSza3rQL6okkw" # あなたのGemini APIキーをペースト

# 正しい引数名 'api_key' を使用してGemini APIを設定
if not GEMINI_API_KEY:
    st.error("Gemini APIキーが設定されていません。Gemini APIを使用できません。")
    st.stop()
genai.configure(api_key=GEMINI_API_KEY)


def get_events_from_db():
    """
    データベースからスケジュールイベントを取得する。
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, start_time, end_time, is_all_day FROM schedules")
    rows = cursor.fetchall()
    conn.close()

    event_list = []
    for row in rows:
        event = {}
        event['id'] = row[0]
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

# --- Streamlitアプリのメイン部分 ---
if os.path.exists(DB_NAME):
    event_list = get_events_from_db()
else:
    event_list = []

st.title('マイカレンダーと予定アドバイス')

# --- 予定計画のアドバイスセクション ---
st.subheader('予定計画のアドバイス')
with st.spinner('アドバイスを生成中...'):
    # ここで新しいアドバイス生成関数を呼び出す
    advice_text = generate_schedule_advice(event_list)
    st.write(advice_text)

# --- 遷移ボタン ---
if st.button('予定を追加'):
    st.switch_page('pages/schedule.py')

options = {
    'initialView': 'dayGridMonth',
    'headerToolbar': {
        'left': 'today prev,next',
        'center': 'title',
        'right': 'dayGridMonth,timeGridWeek,timeGridDay',
    },
    'buttonText': {
        'today': '当日',
        'month': '月ごと',
        'week': '週ごと',
        'day': '日ごと',
        'list': 'リスト'
    },
    'locale': 'ja',
    'firstDay': '0',
}

calendar = st_calendar.calendar(events = event_list, options = options)