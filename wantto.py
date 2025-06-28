import streamlit as st
import pandas as pd
from datetime import date


# ページの基本設定
# ページ全体のレイアウトをワイドモードに設定
st.set_page_config(layout="wide") 


# アプリケーションの状態（セッションステート）を初期化

if 'todo_df' not in st.session_state:
    # 初回起動時に空のDataFrameを作成する
    # スクリーンショットに合わせた列を定義
    initial_df = pd.DataFrame({
        "内容": pd.Series(dtype='str'),
        "期限": pd.Series(dtype='object'), # 日付型を扱うためobject型に
        "進行状況": pd.Series(dtype='str'),
        "優先度": pd.Series(dtype='str'),
    })
    st.session_state.todo_df = initial_df


# メイン画面の構築
st.title("やりたいことリスト")
st.write("表の中を直接編集して、やりたいことを管理しましょう。")

# --- データエディタで表を表示・編集 ---
st.header("リストの編集")

# 編集前のDataFrameをコピーしておく
original_df = st.session_state.todo_df.copy()

# st.data_editor を使ってDataFrameを編集可能な表として表示
edited_df = st.data_editor(
    st.session_state.todo_df,
    # 列ごとの設定
    column_config={
        "内容": st.column_config.TextColumn(
            "内容",
            help="やりたいことの詳細を入力します。",
            required=True, # この列は必須入力にする
        ),
        "期限": st.column_config.DateColumn(
            "期限",
            min_value=date.today(), # 過去の日付は選択不可に
            format="YYYY/MM/DD",
            help="いつまでに達成したいですか？",
        ),
        "進行状況": st.column_config.SelectboxColumn(
            "進行状況",
            help="現在のステータスを選択します。",
            width="medium",
            options=["未着手", "進行中", "完了"],
            required=True,
        ),
        "優先度": st.column_config.SelectboxColumn(
            "優先度",
            help="タスクの優先度を設定します。",
            width="medium",
            options=["高", "中", "低"],
            required=True,
        ),
    },
    num_rows="dynamic", # ユーザーが行を追加・削除できるようにする
    use_container_width=True # ページの幅いっぱいに広げる
)

# 変更の検知と保存処理
# 編集後のDataFrameと元のDataFrameを比較して変更があったか確認
if not edited_df.equals(original_df):
    
    # 「進行状況」が「完了」になった行を特定
    # .isin()を使って元のDFに存在しない完了行を探す
    completed_tasks = edited_df[
        (edited_df["進行状況"] == "完了") & 
        (~edited_df.index.isin(original_df[original_df["進行状況"] == "完了"].index))
    ]

    # 完了したタスクがあればメッセージを表示
    for index, row in completed_tasks.iterrows():
        st.toast(f"🎉 タスク「{row['内容']}」が完了しました！リストから削除されます。")

    # 「完了」以外の行だけをフィルタリングして、session_stateを更新
    # これにより「完了」の行が自動的に削除される
    st.session_state.todo_df = edited_df[edited_df["進行状況"] != "完了"].copy()

    # ページを再実行して、表の表示を即座に更新
    st.experimental_rerun()