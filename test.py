from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, redirect, url_for , session
import question  # 引入 db 模組
import pymysql
import pandas as pd
from io import BytesIO
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "your_secret_key_here"
# 應用程式啟動時初始化資料庫
#question.initialize_database()


try:
    question.update_database()
except pymysql.MySQLError as err:
    print(f"Error initializing database: {err}")

# 設定訂單儲存的資料夾路徑（專案的 static/orders 資料夾）
ORDER_FOLDER = os.path.join(app.root_path, 'static', 'orders')
os.makedirs(ORDER_FOLDER, exist_ok=True)  # 如果資料夾不存在，則建立

@app.route('/')
def home():
    faq_list = question.fetch_all_faq()  # 調用 db 模組的 fetch_all_faq 函數
    return render_template('index.html', faq_list=faq_list)

@app.route('/get_faq/<faq_type>')
def get_faq(faq_type):
    faq_list = question.fetch_all_faq(faq_type=faq_type)
    return jsonify(faq_list)

@app.route("/submit_order_questionnaire", methods=["POST"])
def submit_order_questionnaire():
    # 從表單中獲取訂單數據並保存到 session
    order_data = [
        {"label": "Name", "value": request.form.get("name")},
        {"label": "Phone Number", "value": request.form.get("phone")},
        {"label": "Email Address", "value": request.form.get("email")},
        {"label": "Event Date and Time", "value": request.form.get("event_date_time")},
        {"label": "Event Duration", "value": request.form.get("event_duration")},
        {"label": "Budget", "value": request.form.get("budget")},
        {"label": "Event Type", "value": request.form.get("event_type")},
        {"label": "Event Location", "value": request.form.get("event_location")},
        {"label": "Event End Time", "value": request.form.get("event_end_time")},
        {"label": "Power Hookups", "value": request.form.get("power_hookup")},
        {"label": "Other Food Vendors", "value": request.form.get("other_food_vendors")},
        {"label": "Savory Food Vendors Count", "value": request.form.get("savory_vendors_count")},
        {"label": "Other Food Cuisines", "value": request.form.get("other_food_cuisines")},
        {"label": "Payment Method", "value": request.form.get("payment_method")},
    ]
    session['order_data'] = order_data  # 將訂單數據存入 session

    # 跳轉到確認頁面
    return redirect(url_for("confirm_order"))

@app.route("/confirm_order")
def confirm_order():
    # 從 session 中獲取訂單數據
    order_data = session.get("order_data", {})
    return render_template("confirm_order.html", order_data=order_data)

@app.route("/finalize_order", methods=["POST"])
def finalize_order():
    order_data = session.pop("order_data", {})  # 從 session 中移除訂單數據

   # 生成 PDF 訂單
    if order_data:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"order_{timestamp}.pdf"
        file_path = os.path.join(ORDER_FOLDER, file_name)
        
        # 使用 reportlab 生成 PDF 文件
        generate_pdf(file_path, order_data)

    # 跳轉到感謝頁面
    return redirect(url_for("thank_you"))

@app.route("/thank_you")
def thank_you():
    return render_template("thank_you.html")

# 訂單下載路由
@app.route("/download_order/<file_name>", methods=["GET"])
def download_order(file_name):
    return send_from_directory(ORDER_FOLDER, file_name, as_attachment=True)

def generate_pdf(file_path, order_data):
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # 設置標題
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Order Confirmation")

    # 訂單詳細信息
    c.setFont("Helvetica", 12)
    y_position = height - 150
    for item in order_data:
        c.drawString(100, y_position, f"{item['label']}: {item['value']}")
        y_position -= 20  # 每行之間的間隔

    # 完成 PDF 生成
    c.save()

if __name__ == "__main__":
    app.run()
