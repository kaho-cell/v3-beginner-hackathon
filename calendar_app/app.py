from flask import Flask, render_template, request
import calendar
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def calendar_view():
    # 現在の年と月を取得
    year = request.args.get('year', default=datetime.now().year, type=int)
    month = request.args.get('month', default=datetime.now().month, type=int)
    
    # 月の調整
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1
    
    # カレンダーをHTML形式で作成
    cal = calendar.HTMLCalendar(calendar.SUNDAY)
    calendar_html = cal.formatmonth(year, month)

    # テンプレートにレンダリング
    return render_template('calendar.html', year=year, month=month, calendar_html=calendar_html)

if __name__ == '__main__':
    app.run(debug=True)
