# app.py - СУДАЛГАА БА ЗУРАГ ТЕЛЕГРАМ РУУ ИЛГЭЭХ БҮРЭН КОД
import requests
import base64
import os
from flask import Flask, request, jsonify, render_template

# ====================================================================
# ⚠️ 1. ТАНЫ ТОХИРГОО ⚠️
# ====================================================================
TELEGRAM_TOKEN = '8476306576:AAFIzHzOLDQR_qOKb5yn4eK6VsMmIrGdy_Q'  
# Зөв Групп Чат ID (Сөрөг тоог ашиглана)
CHAT_ID = '-5036234831'
UPLOAD_FOLDER = 'captured_images'
# ====================================================================

app = Flask(__name__)

# Зураг хадгалах хавтас үүсгэх
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ----------------- sendPhoto ЧАДВАРТАЙ ФУНКЦ -----------------
def send_telegram_media_notification(message_text, image_filepath=None):
    """Текст болон зургийг хамт Telegram API руу илгээх функц"""
    
    # sendPhoto-д 'caption' хэрэглэнэ.
    if image_filepath and os.path.exists(image_filepath):
        TELEGRAM_PHOTO_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto'
        payload = {
            'chat_id': CHAT_ID, 
            'caption': message_text, 
            'parse_mode': 'Markdown'
        }
        
        # Зургийн файлыг forms data хэлбэрээр илгээх
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
        # Зураг байхгүй бол зөвхөн текст илгээнэ (sendMessage)
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

# ----------------- Үндсэн Вэб Хаяг (Frontend-ийг үйлчлэх) -----------------
@app.route('/')
def index():
    """http://127.0.0.1:8080/ хаяг руу хандах үед templates/index.html-ийг буцаана"""
    return render_template('index.html') 

# ----------------- Өгөгдөл Хүлээн Авах API -----------------
@app.route('/submit', methods=['POST'])
def submit():
    """Судалгааны хариулт болон мэдээллийг хүлээн авч, Telegram руу илгээнэ."""
    
    # 1. Шинэ name-үүдийг ашиглан хариултуудыг цуглуулах
    role_department = request.form.get('role_department', 'Хариулаагүй') # Шинэ нэр
    profession = request.form.get('profession', 'Хариулаагүй') # Шинэ нэр

    message = (
        f"📋 ШИНЭ СУДАЛГААНЫ ХАРИУЛТ:\n\n"
        f"1) Албан тушаал, Хэлтэс: {role_department}\n"
        f"2) Мэргэжил, Ажлын чиглэл: {profession}\n\n"
        f"--- ТӨХӨӨРӨМЖИЙН МЭДЭЭЛЭЛ ---\n"
        f"📍 IP: {request.remote_addr}\n"
        f"🌐 User-Agent: {request.headers.get('User-Agent')}"
    )
    # ... (үлдсэн Telegram руу илгээх хэсэг өмнөх шигээ)
    # 2. Telegram руу текст мэдээлэл илгээх
    send_text_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    try:
        requests.post(send_text_url, data={'chat_id': CHAT_ID, 'text': message})
    except Exception as e:
        print(f"Telegram API call failed: {e}")

    # 3. Хэрэглэгчийг амжилттай болсны мэдэгдэл рүү шилжүүлэх
    return redirect(url_for('success'))

if __name__ == '__main__':
    # Сервер ажиллуулах
    app.run(port=8080, debug=True)