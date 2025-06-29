# database.py

import sqlite3
import pandas as pd

DB_FILE = "wantto_list.db"
TABLE_NAME = "tasks"

def init_db():
    """データベースを初期化し、テーブルが存在しない場合は作成する"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY,
                内容 TEXT NOT NULL,
                期限 TEXT,
                進行状況 TEXT DEFAULT '未着手',
                優先度 TEXT DEFAULT '中'
            )
        """)
        conn.commit()

def load_all_tasks() -> pd.DataFrame:
    """データベースから全てのタスクを読み込み、idをインデックスとしてDataFrameを返す"""
    with sqlite3.connect(DB_FILE) as conn:
        # index_col='id'で、id列をDataFrameのインデックスとして読み込む
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn, index_col='id')
        if '期限' in df.columns:
            df['期限'] = pd.to_datetime(df['期限'], errors='coerce')
    return df

def save_all_tasks(df: pd.DataFrame):
    """DataFrameの内容でデータベースのテーブル全体を上書きする"""
    with sqlite3.connect(DB_FILE) as conn:
        # index=Trueで、DataFrameのインデックスをデータベースのid列として保存する
        df.to_sql(TABLE_NAME, conn, if_exists='replace', index=True, index_label='id')
        conn.commit()