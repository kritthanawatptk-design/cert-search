import csv
from flask import Flask, render_template_string, request

app = Flask(__name__)


def load_data():
  data = []
  try:
    with open('data.csv', mode='r', encoding='utf-8') as file:
      reader = csv.DictReader(file)
      for row in reader:
        data.append(row)
  except FileNotFoundError:
    pass
  return data


@app.route('/', methods=['GET', 'POST'])
def index():
  results = []
  searched = False
  search_keyword = ''

  if request.method == 'POST':
    search_keyword = request.form.get('search_query', '').strip()
    searched = True
    data = load_data()

    query_lower = search_keyword.lower()
    keywords = [w[:3] for w in query_lower.split() if len(w) >= 2]

    for item in data:
      poster_id = item.get('poster_id', '').strip().lower()
      fullname = item.get('fullname', '').strip().lower()
      cert_title = item.get('cert_title', '').strip().lower()

      combined_text = f'{poster_id} {fullname} {cert_title}'

      matched = False
      if query_lower in combined_text:
        matched = True
      elif keywords:
        if any(kw in combined_text for kw in keywords):
          matched = True

      if matched:
        if item not in results:
          results.append(item)

  html_template = '''
    <!doctype html>
    <html lang="th">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>ระบบค้นหาเกียรติบัตรออนไลน์</title>
        <!-- นำเข้าฟอนต์ Prompt เพื่อความนุ่มนวลและอ่านง่าย -->
        <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600&display=swap" rel="stylesheet">
        <!-- FontAwesome สำหรับไอคอน -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body {
                font-family: 'Prompt', sans-serif;
                /* พื้นหลังโทนสีฟ้าสว่าง สดใส ไม่ทึบ ให้ความรู้สึกสะอาดตาและทันสมัย */
                background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 50%, #7dd3fc 100%);
                background-attachment: fixed;
                color: #0f172a;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                overflow-x: hidden;
                padding: 20px;
            }
            /* เอฟเฟกต์แสงเรืองเบลอฉากหลังให้ดูมีมิติ */
            body::before {
                content: ''; position: absolute; width: 400px; height: 400px;
                background: rgba(255, 255, 255, 0.6); border-radius: 50%;
                top: -100px; left: -100px; filter: blur(80px); z-index: -1;
            }
            body::after {
                content: ''; position: absolute; width: 400px; height: 400px;
                background: rgba(56, 189, 248, 0.3); border-radius: 50%;
                bottom: -100px; right: -100px; filter: blur(80px); z-index: -1;
            }
            /* กล่องหลัก Glassmorphism แบบโปร่งแสง สดใส หรูหรา */
            .container {
                background: rgba(255, 255, 255, 0.75);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.8);
                border-radius: 24px;
                padding: 40px 35px;
                width: 100%;
                max-width: 550px;
                box-shadow: 0 20px 40px rgba(14, 165, 233, 0.15);
                text-align: center;
                animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            }
            @keyframes slideUp {
                0% { opacity: 0; transform: translateY(40px) scale(0.95); }
                100% { opacity: 1; transform: translateY(0) scale(1); }
            }
            .logo-icon { font-size: 42px; color: #0284c7; margin-bottom: 15px; text-shadow: 0 0 15px rgba(2, 132, 199, 0.2); }
            h2 { font-weight: 600; font-size: 24px; margin-bottom: 8px; color: #0f172a; }
            p.subtitle { font-weight: 300; font-size: 13px; color: #475569; margin-bottom: 25px; }
            .input-group { position: relative; margin-bottom: 20px; }
            .input-group i { position: absolute; left: 18px; top: 50%; transform: translateY(-50%); color: #0284c7; }
            input[type="text"] {
                width: 100%; padding: 14px 20px 14px 50px;
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(14, 165, 233, 0.3);
                border-radius: 14px; color: #0f172a; font-family: 'Prompt', sans-serif; font-size: 15px;
                outline: none; transition: all 0.3s ease;
            }
            input[type="text"]::placeholder { color: #94a3b8; }
            input[type="text"]:focus { border-color: #0284c7; background: #ffffff; box-shadow: 0 0 15px rgba(2, 132, 199, 0.2); }
            .btn-search {
                width: 100%; padding: 14px; background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
                color: white; border: none; border-radius: 14px; font-family: 'Prompt', sans-serif;
                font-size: 16px; font-weight: 500; cursor: pointer; transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
            }
            .btn-search:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(14, 165, 233, 0.4); }
            
            .result-container { margin-top: 25px; max-height: 400px; overflow-y: auto; padding-right: 5px; text-align: left; }
            .result-container::-webkit-scrollbar { width: 6px; }
            .result-container::-webkit-scrollbar-thumb { background: rgba(14, 165, 233, 0.2); border-radius: 10px; }

            .result-card {
                margin-bottom: 15px; padding: 18px; background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(14, 165, 233, 0.2); border-radius: 16px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
                animation: fadeInResult 0.5s ease forwards;
            }
            @keyframes fadeInResult { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
            
            .badge { display: inline-block; padding: 4px 10px; font-size: 11px; font-weight: 500; border-radius: 6px; margin-bottom: 8px; }
            .badge-award { background: rgba(234, 179, 8, 0.15); color: #ca8a04; border: 1px solid rgba(234, 179, 8, 0.3); }
            .badge-participant { background: rgba(14, 165, 233, 0.15); color: #0284c7; border: 1px solid rgba(14, 165, 233, 0.3); }

            .result-card p { font-size: 13px; margin-bottom: 6px; color: #334155; font-weight: 300; line-height: 1.4; }
            .result-card p strong { color: #0f172a; font-weight: 500; }
            
            .btn-download {
                display: block; width: 100%; margin-top: 12px; padding: 10px;
                background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white;
                text-decoration: none; border-radius: 10px; font-weight: 500; font-size: 13px; text-align: center;
                transition: all 0.3s ease;
                box-shadow: 0 4px 10px rgba(16, 185, 129, 0.2);
            }
            .btn-download:hover { background: linear-gradient(135deg, #34d399 0%, #047857 100%); }
            
            .summary-text { font-size: 13px; color: #0284c7; margin-bottom: 12px; font-weight: 500; }
            .not-found {
                margin-top: 20px; padding: 15px; background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 12px; color: #dc2626; font-size: 14px; text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo-icon"><i class="fa-solid fa-award"></i></div>
            <h2>ระบบค้นหาเกียรติบัตร</h2>
            <p class="subtitle">ค้นหาเกียรติบัตรรางวัลและเกียรติบัตรเข้าร่วมงาน</p>
            
            <form method="POST">
                <div class="input-group">
                    <i class="fa-solid fa-magnifying-glass"></i>
                    <input type="text" name="search_query" value="{{ search_keyword }}" placeholder="ค้นหาด้วยเลขที่โปสเตอร์ หรือ ใส่ชื่อผู้นำเสนอ" required>
                </div>
                <button type="submit" class="btn-search">
                    <i class="fa-solid fa-search" style="margin-right: 8px;"></i> ค้นหาเกียรติบัตร
                </button>
            </form>

            {% if searched %}
                {% if results %}
                    <div class="result-container">
                        <p class="summary-text"><i class="fa-solid fa-circle-check"></i> ค้นพบทั้งหมด <strong>{{ results|length }}</strong> รายการ:</p>
                        {% for item in results %}
                            <div class="result-card">
                                {% if item.cert_type == 'award' %}
                                    <span class="badge badge-award"><i class="fa-solid fa-trophy"></i> เกียรติบัตรรางวัล</span>
                                {% else %}
                                    <span class="badge badge-participant"><i class="fa-solid fa-user-check"></i> เกียรติบัตรเข้าร่วมงาน</span>
                                {% endif %}
                                <p><strong>รหัสโปสเตอร์:</strong> {{ item.poster_id }}</p>
                                <p><strong>ชื่อผู้รับ:</strong> {{ item.fullname }}</p>
                                <p><strong>ชื่อเรื่อง:</strong> {{ item.cert_title }}</p>
                                <a href="{{ item.file_link }}" target="_blank" class="btn-download">
                                    <i class="fa-solid fa-cloud-arrow-down" style="margin-right: 6px;"></i> ดาวน์โหลดเกียรติบัตรใบนี้
                                </a>
                            </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="not-found">
                        <i class="fa-solid fa-circle-exclamation"></i> ไม่พบข้อมูลเกียรติบัตรสำหรับคำค้นหานี้ กรุณาตรวจสอบชื่อหรือรหัสใหม่อีกครั้ง
                    </div>
                {% endif %}
            {% endif %}
        </div>
    </body>
    </html>
    '''
  return render_template_string(
      html_template,
      results=results,
      searched=searched,
      search_keyword=search_keyword,
  )


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)