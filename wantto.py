# wantto.py

import streamlit as st
import database
# ご指定の形式でインポート
from streamlit.column_config import TextColumn, DateColumn, SelectboxColumn
from datetime import date

def render_todo_editor():
    """
    タスクの編集・追加・削除を一つのデータエディタで行うためのUIを描画する
    """
    st.header("やりたいことリスト（編集・追加）")
    st.info("表を直接編集したり、下の「＋」ボタンで行を追加できます。「進行状況」を「完了」にすると保存時に削除されます。")

    with st.form(key="unified_form"):
        tasks_df = database.load_all_tasks()
        tasks_df_no_index = tasks_df.reset_index()

        edited_df_no_index = st.data_editor(
            tasks_df_no_index,
            column_config={
                "id": None, # ID列は表示しない
                # インポート形式の変更を反映
                "内容": TextColumn("内容", required=True, width="large"),
                "期限": DateColumn("期限", format="YYYY/MM/DD"),
                "進行状況": SelectboxColumn("進行状況", options=["未着手", "進行中", "完了"], required=True),
                "優先度": SelectboxColumn("優先度", options=["高", "中", "低"], required=True),
            },
            use_container_width=True,
            num_rows="dynamic",
            key="editor",
            hide_index=True
        )
        
        submitted = st.form_submit_button("すべての変更を保存")

    if submitted:
        edited_df_with_index = edited_df_no_index.set_index('id')
        final_df = edited_df_with_index[edited_df_with_index['進行状況'] != '完了'].copy()
        
        database.save_all_tasks(final_df)
        st.toast("✅ 保存しました！")
        st.rerun()