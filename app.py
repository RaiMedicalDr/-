from flask import Flask, request, jsonify
import json
from datetime import datetime, timedelta

app = Flask(__name__)

DATA_FILE = 'medication_data.json'

def load_medication_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_medication_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    data = load_medication_data()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 今日のデータがない場合は初期化
    if today not in data:
        data[today] = {
            "morning-inhalation": False,
            "morning-blood-pressure": False,
            "morning-allergy": False,
            "evening-inhalation": False,
            "evening-blood-pressure": False,
            "evening-allergy": False
        }
        save_medication_data(data)
    
    medication_data = data[today]
    # HTMLを直接文字列で返す
    return f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>お薬チェックアプリ</title>
        <style>
            body {{
                font-family: 'Hiragino Kaku Gothic ProN', 'ヒラギノ角ゴ ProN W3', sans-serif;
                background-color: #f0f8ff;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                line-height: 1.6;
            }}
            .container {{
                background-color: white;
                border-radius: 20px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                padding: 30px;
                width: 90%;
                max-width: 600px;
            }}
            h1 {{
                color: #2c3e50;
                text-align: center;
                font-size: 2.5em;
                margin-bottom: 20px;
            }}
            .day-section {{
                background-color: #e6f2ff;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            .day-title {{
                font-size: 1.5em;
                color: #3498db;
                margin-bottom: 15px;
                text-align: center;
            }}
            .medication-group {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 15px;
            }}
            .medication-item {{
                display: flex;
                align-items: center;
            }}
            .medication-item label {{
                font-size: 1.2em;
                margin-right: 10px;
            }}
            .checkbox {{
                width: 30px;
                height: 30px;
                cursor: pointer;
            }}
            a {{
                text-decoration: none;
                color: #3498db;
                display: block;
                text-align: center;
                margin-top: 20px;
            }}
        </style>
        <script>
            document.addEventListener('DOMContentLoaded', () => {{
                const medicationData = {json.dumps(medication_data)};
                for (const [key, value] of Object.entries(medicationData)) {{
                    const checkbox = document.getElementById(key);
                    if (checkbox) {{
                        checkbox.checked = value;
                        checkbox.disabled = value; // 1日中チェックは変更できない
                    }}
                }}

                document.querySelectorAll('.checkbox').forEach(checkbox => {{
                    checkbox.addEventListener('change', (event) => {{
                        const medicationType = event.target.id;
                        const isChecked = event.target.checked;

                        fetch('/track_medication', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json'
                            }},
                            body: JSON.stringify({{
                                medication_type: medicationType,
                                is_checked: isChecked
                            }})
                        }}).then(response => response.json())
                          .then(data => console.log(data));
                    }});
                }});
            }});
        </script>
    </head>
    <body>
        <div class="container">
            <h1>お薬チェックカレンダー</h1>
            <div class="day-section">
                <div class="day-title">朝のお薬</div>
                <div class="medication-group">
                    <div class="medication-item">
                        <label for="morning-inhalation">吸入</label>
                        <input type="checkbox" class="checkbox" id="morning-inhalation">
                    </div>
                    <div class="medication-item">
                        <label for="morning-blood-pressure">血圧薬</label>
                        <input type="checkbox" class="checkbox" id="morning-blood-pressure">
                    </div>
                    <div class="medication-item">
                        <label for="morning-allergy">アレルギー薬</label>
                        <input type="checkbox" class="checkbox" id="morning-allergy">
                    </div>
                </div>
            </div>
            <div class="day-section">
                <div class="day-title">夜のお薬</div>
                <div class="medication-group">
                    <div class="medication-item">
                        <label for="evening-inhalation">吸入</label>
                        <input type="checkbox" class="checkbox" id="evening-inhalation">
                    </div>
                    <div class="medication-item">
                        <label for="evening-blood-pressure">血圧薬</label>
                        <input type="checkbox" class="checkbox" id="evening-blood-pressure">
                    </div>
                    <div class="medication-item">
                        <label for="evening-allergy">アレルギー薬</label>
                        <input type="checkbox" class="checkbox" id="evening-allergy">
                    </div>
                </div>
            </div>
            <a href="/history">過去7日間の履歴を見る</a>
        </div>
    </body>
    </html>
    """

@app.route('/history')
def history():
    data = load_medication_data()
    today = datetime.now()
    history = {}
    
    for i in range(7):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        if date in data:
            history[date] = data[date]
    
    # HTML文字列を生成
    history_html = "<!DOCTYPE html><html lang='ja'><head><meta charset='UTF-8'><title>過去7日間の履歴</title></head><body>"
    history_html += "<h1>過去7日間の履歴</h1>"
    for date, medications in history.items():
        history_html += f"<div><h3>{date}</h3><ul>"
        for med, status in medications.items():
            status_text = "✓" if status else "✗"
            history_html += f"<li>{med}: {status_text}</li>"
        history_html += "</ul></div>"
    history_html += "<a href='/'>戻る</a></body></html>"
    
    return history_html

@app.route('/track_medication', methods=['POST'])
def track_medication():
    data = load_medication_data()
    today = datetime.now().strftime('%Y-%m-%d')
    
    medication_type = request.json['medication_type']
    is_checked = request.json['is_checked']
    
    # 今日のデータを更新
    if today not in data:
        data[today] = {}
    data[today][medication_type] = is_checked
    
    save_medication_data(data)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)