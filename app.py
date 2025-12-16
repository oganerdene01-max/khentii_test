# app.py - СУДАЛГАА БА ЗУРАГ ТЕЛЕГРАМ РУУ ИЛГЭЭХ БҮРЭН КОД
import requests
import base64
import os
# redirect болон url_for-ийг нэмж импортлов
from flask import Flask, request, jsonify, render_template, redirect, url_for 

# ====================================================================
# ⚠️ 1. ТАНЫ ТОХИРГОО: RENDER PRODUCTION-Д ЗОРИУЛЖ ӨӨРЧИЛЛӨӨ ⚠️
# ====================================================================

# Render Environment Variables-аас нууц үгсийг авна
# Хэрэв DEV (local) орчин бол энд хатуу бичсэн утгыг ашиглана (Туршилтад зориулж)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8476306576:AAFIzHzOLDQR_qOKb5yn4eK6VsMmIrGdy_Q')  
CHAT_ID = os.environ.get('CHAT_ID', '-5036234831')
UPLOAD_FOLDER = 'captured_images'
# ====================================================================

app = Flask(__name__)

# Зураг хадгалах хавтас үүсгэх (Render дээр түр хадгалах)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ----------------- sendPhoto ЧАДВАРТАЙ ФУНКЦ -----------------
# (Энэ функц submit() дотор ашиглагдаагүй тул хуучин байдлаар үлдээв)
def send_telegram_media_notification(message_text, image_filepath=None):
    """Текст болон зургийг хамт Telegram API руу илгээх функц"""
    # ... (код хэвээр) ...
    if image_filepath and os.path.exists(image_filepath):
        TELEGRAM_PHOTO_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto'
        payload = {
            'chat_id': CHAT_ID, 
            'caption': message_text, 
            'parse_mode': 'Markdown'
        }
        files = {'photo': open(image_filepath, 'rb')}
        
        try:
            response = requests.post(TELEGRAM_PHOTO_API_URL, data=payload, files=files)
            response.raise_for_status()
            print("Telegram-д зураг болон текст амжилттай илгээгдлээ.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Telegram API руу зураг илгээх алдаа: {e}")
            return False
    else:
        TELEGRAM_MESSAGE_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        payload_text_only = {
            'chat_id': CHAT_ID, 
            'text': message_text, 
            'parse_mode': 'Markdown'
        }
        try:
            response = requests.post(TELEGRAM_MESSAGE_API_URL, json=payload_text_only)
            response.raise_for_status()
            print("Telegram-д зөвхөн текст амжилттай илгээгдлээ.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Telegram API руу зөвхөн текст илгээх алдаа: {e}")
            return False


# ----------------- Үндсэн Вэб Хаяг -----------------
@app.route('/')
def index():
    return render_template('index.html') 

# ----------------- Амжилттай Илгээсэн Хуудас -----------------
@app.route('/success')
def success():
    """Амжилттай илгээсэн хуудас (Хэрэглэгчийн харах хуудас)."""
    return """
    <div style='text-align: center; padding: 50px; font-family: Arial;'>
        <h1 style='color: green;'>✅ Баярлалаа!</h1>
        <p style='font-size: 18px;'>Таны хариулт амжилттай илгээгдлээ. Бид таны саналд талархаж байна.</p>
        <p style='margin-top: 20px; color: #666;'>Та энэ хуудсыг хааж болно.</p>
    </div>
    """

# ----------------- Өгөгдөл Хүлээн Авах API -----------------
@app.route('/submit', methods=['POST'])
def submit():
    """Судалгааны хариулт болон мэдээллийг хүлээн авч, Telegram руу илгээнэ."""
    
    # 1. name-үүдийг ашиглан хариултуудыг цуглуулах
    role_department = request.form.get('role_department', 'Хариулаагүй')
    profession = request.form.get('profession', 'Хариулаагүй')

    message = (
        f"📋 ШИНЭ СУДАЛГААНЫ ХАРИУЛТ:\n\n"
        f"1) Албан тушаал, Хэлтэс: {role_department}\n"
        f"2) Мэргэжил, Ажлын чиглэл: {profession}\n\n"
        f"--- ТӨХӨӨРӨМЖИЙН МЭДЭЭЛЭЛ ---\n"
        f"📍 IP: {request.remote_addr}\n"
        f"🌐 User-Agent: {request.headers.get('User-Agent')}"
    )
    
    # 2. Telegram руу текст мэдээлэл илгээх (sendMessage функцээр хийвэл илүү хялбар)
    send_telegram_media_notification(message) # Энд зөвхөн текст илгээнэ

    # 3. Хэрэглэгчийг амжилттай болсны мэдэгдэл рүү шилжүүлэх
    return redirect(url_for('success'))

if __name__ == '__main__':
    # Local туршилтад зориулав
    app.run(port=8080, debug=True)

# Render-д зориулсан Production Run Configuration
# Энэ нь Procfile-д (gunicorn app:app) ашиглагдана
# Үйлдвэрлэлийн орчинд PORT хувьсагчийг os.environ-с авах ёстой.
# port = int(os.environ.get('PORT', 5000))
# app.run(host='0.0.0.0', port=port)