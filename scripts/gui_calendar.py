#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import calendar
import datetime
import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class Event:
    id: str
    title: str
    description: str
    date: str  # YYYY-MM-DD format
    time: str  # HH:MM format
    category: str
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class CalendarGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📅 Python カレンダー予定管理")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # データファイル
        self.data_file = "events.json"
        self.events: List[Event] = []
        
        # 現在の表示月
        self.current_date = datetime.date.today()
        self.selected_date = datetime.date.today()
        
        # カテゴリの色設定
        self.category_colors = {
            "仕事": "#FF6B6B",
            "個人": "#4ECDC4", 
            "会議": "#45B7D1",
            "その他": "#96CEB4"
        }
        
        # GUI初期化
        self.setup_gui()
        self.load_events()
        self.update_calendar()
        self.update_event_list()
    
    def setup_gui(self):
        """GUIコンポーネントの設定"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ウィンドウのリサイズ設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 左側：カレンダー部分
        calendar_frame = ttk.LabelFrame(main_frame, text="📅 カレンダー", padding="10")
        calendar_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # カレンダーナビゲーション
        nav_frame = ttk.Frame(calendar_frame)
        nav_frame.grid(row=0, column=0, columnspan=7, pady=(0, 10), sticky=(tk.W, tk.E))
        
        ttk.Button(nav_frame, text="◀", command=self.prev_month).grid(row=0, column=0)
        self.month_label = ttk.Label(nav_frame, font=("Arial", 14, "bold"))
        self.month_label.grid(row=0, column=1, padx=20)
        ttk.Button(nav_frame, text="▶", command=self.next_month).grid(row=0, column=2)
        ttk.Button(nav_frame, text="今日", command=self.go_to_today).grid(row=0, column=3, padx=(20, 0))
        
        # 曜日ヘッダー
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        for i, day in enumerate(weekdays):
            label = ttk.Label(calendar_frame, text=day, font=("Arial", 10, "bold"))
            label.grid(row=1, column=i, padx=2, pady=2)
        
        # カレンダーグリッド
        self.calendar_buttons = []
        for week in range(6):
            week_buttons = []
            for day in range(7):
                btn = tk.Button(calendar_frame, width=8, height=4, 
                              command=lambda w=week, d=day: self.select_date(w, d),
                              font=("Arial", 9))
                btn.grid(row=week+2, column=day, padx=1, pady=1)
                week_buttons.append(btn)
            self.calendar_buttons.append(week_buttons)
        
        # 右上：予定リスト
        event_frame = ttk.LabelFrame(main_frame, text="📋 選択日の予定", padding="10")
        event_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        event_frame.columnconfigure(0, weight=1)
        event_frame.rowconfigure(1, weight=1)
        
        # 選択日表示
        self.selected_date_label = ttk.Label(event_frame, font=("Arial", 12, "bold"))
        self.selected_date_label.grid(row=0, column=0, pady=(0, 10))
        
        # 予定リスト
        list_frame = ttk.Frame(event_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview for events
        columns = ("時間", "タイトル", "カテゴリ")
        self.event_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.event_tree.heading(col, text=col)
            self.event_tree.column(col, width=100)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.event_tree.yview)
        self.event_tree.configure(yscrollcommand=scrollbar.set)
        
        self.event_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 予定操作ボタン
        button_frame = ttk.Frame(event_frame)
        button_frame.grid(row=2, column=0, pady=(10, 0))
        
        ttk.Button(button_frame, text="➕ 予定追加", command=self.add_event).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="✏️ 編集", command=self.edit_event).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="🗑️ 削除", command=self.delete_event).grid(row=0, column=2, padx=5)
        
        # 右下：統計・その他
        stats_frame = ttk.LabelFrame(main_frame, text="📊 統計情報", padding="10")
        stats_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.stats_text = tk.Text(stats_frame, height=8, width=40, font=("Arial", 9))
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        stats_scroll = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scroll.set)
        stats_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # メニューバー
        self.setup_menu()
    
    def setup_menu(self):
        """メニューバーの設定"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # ファイルメニュー
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="バックアップ作成", command=self.create_backup)
        file_menu.add_command(label="CSVエクスポート", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self.root.quit)
        
        # 表示メニュー
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="表示", menu=view_menu)
        view_menu.add_command(label="今月に移動", command=self.go_to_today)
        view_menu.add_command(label="統計更新", command=self.update_statistics)
        
        # ヘルプメニュー
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ヘルプ", menu=help_menu)
        help_menu.add_command(label="使い方", command=self.show_help)
        help_menu.add_command(label="バージョン情報", command=self.show_about)
    
    def load_events(self):
        """JSONファイルから予定を読み込み"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.events = [Event.from_dict(event) for event in data]
            except (json.JSONDecodeError, KeyError) as e:
                messagebox.showerror("エラー", f"データファイルの読み込みエラー: {e}")
                self.events = []
    
    def save_events(self):
        """予定をJSONファイルに保存"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([event.to_dict() for event in self.events], f, 
                         ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("エラー", f"データファイルの保存エラー: {e}")
    
    def update_calendar(self):
        """カレンダー表示を更新"""
        # 月ラベル更新
        self.month_label.config(text=f"{self.current_date.year}年{self.current_date.month}月")
        
        # カレンダーデータ取得
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        # 全ボタンをクリア
        for week_buttons in self.calendar_buttons:
            for btn in week_buttons:
                btn.config(text="", state="disabled", bg="SystemButtonFace")
        
        # 日付ボタンを設定
        for week_idx, week in enumerate(cal):
            for day_idx, day in enumerate(week):
                btn = self.calendar_buttons[week_idx][day_idx]
                if day == 0:
                    btn.config(text="", state="disabled", bg="SystemButtonFace")
                else:
                    btn.config(text=str(day), state="normal")
                    
                    # 日付オブジェクト作成
                    date_obj = datetime.date(self.current_date.year, self.current_date.month, day)
                    
                    # 今日の日付をハイライト
                    if date_obj == datetime.date.today():
                        btn.config(bg="#FFE4B5", font=("Arial", 9, "bold"))
                    # 選択された日付をハイライト
                    elif date_obj == self.selected_date:
                        btn.config(bg="#87CEEB", font=("Arial", 9, "bold"))
                    # 予定がある日をハイライト
                    elif self.has_events_on_date(date_obj):
                        btn.config(bg="#98FB98", font=("Arial", 9))
                    else:
                        btn.config(bg="white", font=("Arial", 9))
    
    def has_events_on_date(self, date_obj):
        """指定した日に予定があるかチェック"""
        date_str = date_obj.strftime("%Y-%m-%d")
        return any(event.date == date_str for event in self.events)
    
    def select_date(self, week, day):
        """日付を選択"""
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        if week < len(cal) and day < len(cal[week]) and cal[week][day] != 0:
            self.selected_date = datetime.date(self.current_date.year, self.current_date.month, cal[week][day])
            self.update_calendar()
            self.update_event_list()
    
    def update_event_list(self):
        """選択日の予定リストを更新"""
        # 選択日ラベル更新
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        weekday = weekdays[self.selected_date.weekday()]
        self.selected_date_label.config(
            text=f"{self.selected_date.year}年{self.selected_date.month}月{self.selected_date.day}日 ({weekday})"
        )
        
        # 予定リストクリア
        for item in self.event_tree.get_children():
            self.event_tree.delete(item)
        
        # 選択日の予定を取得
        date_str = self.selected_date.strftime("%Y-%m-%d")
        day_events = [event for event in self.events if event.date == date_str]
        day_events.sort(key=lambda x: x.time)
        
        # 予定をTreeviewに追加
        for event in day_events:
            # カテゴリに応じてタグを設定
            tag = event.category
            self.event_tree.insert("", "end", values=(event.time, event.title, event.category), 
                                 tags=(tag, event.id))
        
        # カテゴリ別の色設定
        for category, color in self.category_colors.items():
            self.event_tree.tag_configure(category, background=color, foreground="white")
    
    def prev_month(self):
        """前月に移動"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year-1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month-1)
        self.update_calendar()
    
    def next_month(self):
        """次月に移動"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year+1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month+1)
        self.update_calendar()
    
    def go_to_today(self):
        """今日の日付に移動"""
        today = datetime.date.today()
        self.current_date = today
        self.selected_date = today
        self.update_calendar()
        self.update_event_list()
    
    def add_event(self):
        """予定追加ダイアログ"""
        dialog = EventDialog(self.root, "予定追加")
        if dialog.result:
            event_data = dialog.result
            event_data['date'] = self.selected_date.strftime("%Y-%m-%d")
            event_data['id'] = str(int(datetime.datetime.now().timestamp() * 1000))
            
            event = Event.from_dict(event_data)
            self.events.append(event)
            self.save_events()
            self.update_calendar()
            self.update_event_list()
            self.update_statistics()
            messagebox.showinfo("成功", "予定を追加しました")
    
    def edit_event(self):
        """予定編集"""
        selection = self.event_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "編集する予定を選択してください")
            return
        
        # 選択された予定のIDを取得
        item = selection[0]
        tags = self.event_tree.item(item, "tags")
        event_id = tags[1] if len(tags) > 1 else None
        
        if not event_id:
            messagebox.showerror("エラー", "予定IDが見つかりません")
            return
        
        # 予定を検索
        event = next((e for e in self.events if e.id == event_id), None)
        if not event:
            messagebox.showerror("エラー", "予定が見つかりません")
            return
        
        # 編集ダイアログ
        dialog = EventDialog(self.root, "予定編集", event)
        if dialog.result:
            # 予定を更新
            for key, value in dialog.result.items():
                setattr(event, key, value)
            
            self.save_events()
            self.update_calendar()
            self.update_event_list()
            self.update_statistics()
            messagebox.showinfo("成功", "予定を更新しました")
    
    def delete_event(self):
        """予定削除"""
        selection = self.event_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "削除する予定を選択してください")
            return
        
        if messagebox.askyesno("確認", "選択した予定を削除しますか？"):
            item = selection[0]
            tags = self.event_tree.item(item, "tags")
            event_id = tags[1] if len(tags) > 1 else None
            
            if event_id:
                self.events = [e for e in self.events if e.id != event_id]
                self.save_events()
                self.update_calendar()
                self.update_event_list()
                self.update_statistics()
                messagebox.showinfo("成功", "予定を削除しました")
    
    def update_statistics(self):
        """統計情報を更新"""
        self.stats_text.delete(1.0, tk.END)
        
        if not self.events:
            self.stats_text.insert(tk.END, "予定データがありません")
            return
        
        # 基本統計
        total_events = len(self.events)
        self.stats_text.insert(tk.END, f"📊 統計情報\n")
        self.stats_text.insert(tk.END, f"{'='*30}\n")
        self.stats_text.insert(tk.END, f"総予定数: {total_events}件\n\n")
        
        # カテゴリ別統計
        from collections import Counter
        categories = [event.category for event in self.events]
        category_counts = Counter(categories)
        
        self.stats_text.insert(tk.END, "📋 カテゴリ別予定数:\n")
        for category, count in category_counts.most_common():
            percentage = (count / total_events) * 100
            self.stats_text.insert(tk.END, f"  {category}: {count}件 ({percentage:.1f}%)\n")
        
        # 今月の予定
        current_month = self.current_date.strftime("%Y-%m")
        month_events = [e for e in self.events if e.date.startswith(current_month)]
        self.stats_text.insert(tk.END, f"\n📅 今月の予定: {len(month_events)}件\n")
        
        # 今日の予定
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        today_events = [e for e in self.events if e.date == today_str]
        self.stats_text.insert(tk.END, f"📅 今日の予定: {len(today_events)}件\n")
    
    def create_backup(self):
        """バックアップ作成"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"events_backup_{timestamp}.json"
            
            import shutil
            shutil.copy2(self.data_file, backup_filename)
            messagebox.showinfo("成功", f"バックアップを作成しました:\n{backup_filename}")
        except Exception as e:
            messagebox.showerror("エラー", f"バックアップ作成に失敗しました: {e}")
    
    def export_csv(self):
        """CSV エクスポート"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"events_export_{timestamp}.csv"
            
            with open(csv_filename, 'w', encoding='utf-8') as f:
                f.write("ID,タイトル,詳細,日付,時間,カテゴリ\n")
                for event in self.events:
                    title = event.title.replace('"', '""')
                    description = event.description.replace('"', '""')
                    f.write(f'"{event.id}","{title}","{description}","{event.date}","{event.time}","{event.category}"\n')
            
            messagebox.showinfo("成功", f"CSVファイルをエクスポートしました:\n{csv_filename}")
        except Exception as e:
            messagebox.showerror("エラー", f"CSVエクスポートに失敗しました: {e}")
    
    def show_help(self):
        """ヘルプ表示"""
        help_text = """
📅 Python カレンダー予定管理 - 使い方

【基本操作】
• カレンダーの日付をクリックして選択
• ◀▶ ボタンで月を移動
• 「今日」ボタンで今日の日付に移動

【予定管理】
• ➕予定追加: 新しい予定を追加
• ✏️編集: 選択した予定を編集
• 🗑️削除: 選択した予定を削除

【カレンダーの色】
• オレンジ: 今日の日付
• 青: 選択中の日付  
• 緑: 予定がある日

【メニュー】
• ファイル → バックアップ作成/CSVエクスポート
• 表示 → 統計更新
"""
        messagebox.showinfo("使い方", help_text)
    
    def show_about(self):
        """バージョン情報"""
        about_text = """
📅 Python カレンダー予定管理
Version 1.0

Pythonとtkinterで作成された
シンプルで使いやすい予定管理ツールです。

© 2024 Python Calendar Scheduler
"""
        messagebox.showinfo("バージョン情報", about_text)

class EventDialog:
    def __init__(self, parent, title, event=None):
        self.result = None
        
        # ダイアログウィンドウ作成
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 中央に配置
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # フォーム作成
        self.create_form(event)
        
        # ダイアログが閉じられるまで待機
        self.dialog.wait_window()
    
    def create_form(self, event):
        """フォーム作成"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        ttk.Label(main_frame, text="タイトル:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.title_var = tk.StringVar(value=event.title if event else "")
        ttk.Entry(main_frame, textvariable=self.title_var, width=40).grid(row=0, column=1, pady=(0, 5))
        
        # 時間
        ttk.Label(main_frame, text="時間:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.time_var = tk.StringVar(value=event.time if event else "09:00")
        ttk.Entry(main_frame, textvariable=self.time_var, width=40).grid(row=1, column=1, pady=(0, 5))
        
        # カテゴリ
        ttk.Label(main_frame, text="カテゴリ:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.category_var = tk.StringVar(value=event.category if event else "その他")
        category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, 
                                    values=["仕事", "個人", "会議", "その他"], width=37)
        category_combo.grid(row=2, column=1, pady=(0, 5))
        
        # 詳細
        ttk.Label(main_frame, text="詳細:").grid(row=3, column=0, sticky=(tk.W, tk.N), pady=(0, 5))
        self.description_text = tk.Text(main_frame, width=30, height=6)
        self.description_text.grid(row=3, column=1, pady=(0, 10))
        if event and event.description:
            self.description_text.insert(1.0, event.description)
        
        # ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="保存", command=self.save_event).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="キャンセル", command=self.dialog.destroy).grid(row=0, column=1)
    
    def save_event(self):
        """予定保存"""
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("エラー", "タイトルを入力してください")
            return
        
        time = self.time_var.get().strip()
        if not time:
            messagebox.showerror("エラー", "時間を入力してください")
            return
        
        # 時間形式チェック
        try:
            datetime.datetime.strptime(time, "%H:%M")
        except ValueError:
            messagebox.showerror("エラー", "時間は HH:MM 形式で入力してください")
            return
        
        self.result = {
            'title': title,
            'time': time,
            'category': self.category_var.get(),
            'description': self.description_text.get(1.0, tk.END).strip()
        }
        
        self.dialog.destroy()

def main():
    root = tk.Tk()
    app = CalendarGUI(root)
    
    # 統計情報を初期化
    app.update_statistics()
    
    root.mainloop()

if __name__ == "__main__":
    main()
