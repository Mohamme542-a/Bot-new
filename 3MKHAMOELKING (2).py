
# ======================
# 🔀 خلط الأرقام لتجنب التكرار
# ======================
def shuffle_numbers(numbers):
    try:
        random.shuffle(numbers)
    except:
        pass
    return numbers

import time
import requests
import json
import re
import os
from datetime import datetime, date, timedelta
from pathlib import Path
import sqlite3
import telebot
from telebot import types
import threading
import random
import traceback

# ======================
# 🔐 إعدادات API الأساسية
# ======================
API_PANELS = [
    {
        "url": "http://147.135.212.197/crapi/time/viewstats",
        "token": "QlBWQTRSQoVyT1VGiHRnfHlXmIdgbJCEYoOXRWRUk2hlcmp9eopu="
    },
    {
        "url": "http://147.135.212.197/crapi/time/viewstats",  # ضع رابط اللوحة الثانية هنا
        "token": "SE9XNEVBlWGIbYpzVVFwZoVOVUmBjJBhR4xvZFaVin5EjZRafl8=" # ضع توكن اللوحة الثانية هنا
    }
]

# سيتم استخدام أول لوحة افتراضياً إذا لم يتم تعديل الكود في الأسفل
API_URL = API_PANELS[0]["url"]
API_TOKEN = API_PANELS[0]["token"]


# ======================
# 🔗 إعدادات الروابط والقنوات
# ======================
CHANNEL_1_URL = "https://t.me/gvbhvc669"
CHANNEL_2_URL = "https://t.me/fhbcf5888"
OWNER_1_LINK = "t.me/nox_matrix"
OWNER_2_LINK = "t.me/nox_matrix"

# ======================
# 🤖 إعدادات البوت
# ======================
BOT_TOKEN = "8626823127:AAEzStnVxEsOyIl_3SGZKLdMpKUDNNYZCmo"
CHAT_IDS = ["-1003819039558"]
REFRESH_INTERVAL = 2
ADMIN_IDS = [7502009864 ,]
OWNER_ID = 7502009864
DB_PATH = "/app/bot.db"

# ======================
# 🗺️ أكواد الدول المحدثة
# ======================
COUNTRY_CODES = {
    "1": ("USA/Canada", "🇺🇸"),
    "7": ("Kazakhstan", "🇰🇿"),
    "20": ("Egypt", "🇪🇬"),
    "27": ("South Africa", "🇿🇦"),
    "30": ("Greece", "🇬🇷"),
    "31": ("Netherlands", "🇳🇱"),
    "32": ("Belgium", "🇧🇪"),
    "33": ("France", "🇫🇷"),
    "34": ("Spain", "🇪🇸"),
    "36": ("Hungary", "🇭🇺"),
    "39": ("Italy", "🇮🇹"),
    "40": ("Romania", "🇷🇴"),
    "41": ("Switzerland", "🇨🇭"),
    "43": ("Austria", "🇦🇹"),
    "44": ("UK", "🇬🇧"),
    "45": ("Denmark", "🇩🇰"),
    "46": ("Sweden", "🇸🇪"),
    "47": ("Norway", "🇳🇴"),
    "48": ("Poland", "🇵🇱"),
    "49": ("Germany", "🇩🇪"),
    "51": ("Peru", "🇵🇪"),
    "52": ("Mexico", "🇲🇽"),
    "53": ("Cuba", "🇨🇺"),
    "54": ("Argentina", "🇦🇷"),
    "55": ("Brazil", "🇧🇷"),
    "56": ("Chile", "🇨🇱"),
    "57": ("Colombia", "🇨🇴"),
    "58": ("Venezuela", "🇻🇪"),
    "60": ("Malaysia", "🇲🇾"),
    "61": ("Australia", "🇦🇺"),
    "62": ("Indonesia", "🇮🇩"),
    "63": ("Philippines", "🇵🇭"),
    "64": ("New Zealand", "🇳🇿"),
    "65": ("Singapore", "🇸🇬"),
    "66": ("Thailand", "🇹🇭"),
    "81": ("Japan", "🇯🇵"),
    "82": ("South Korea", "🇰🇷"),
    "84": ("Vietnam", "🇻🇳"),
    "86": ("China", "🇨🇳"),
    "90": ("Turkey", "🇹🇷"),
    "91": ("India", "🇮🇳"),
    "92": ("Pakistan", "🇵🇰"),
    "93": ("Afghanistan", "🇦🇫"),
    "94": ("Sri Lanka", "🇱🇰"),
    "95": ("Myanmar", "🇲🇲"),
    "98": ("Iran", "🇮🇷"),
    "211": ("South Sudan", "🇸🇸"),
    "212": ("Morocco", "🇲🇦"),
    "213": ("Algeria", "🇩🇿"),
    "216": ("Tunisia", "🇹🇳"),
    "218": ("Libya", "🇱🇾"),
    "220": ("Gambia", "🇬🇲"),
    "221": ("Senegal", "🇸🇳"),
    "222": ("Mauritania", "🇲🇷"),
    "223": ("Mali", "🇲🇱"),
    "224": ("Guinea", "🇬🇳"),
    "225": ("Ivory Coast", "🇨🇮"),
    "226": ("Burkina Faso", "🇧🇫"),
    "227": ("Niger", "🇳🇪"),
    "228": ("Togo", "🇹🇬"),
    "229": ("Benin", "🇧🇯"),
    "230": ("Mauritius", "🇲🇺"),
    "231": ("Liberia", "🇱🇷"),
    "232": ("Sierra Leone", "🇸🇱"),
    "233": ("Ghana", "🇬🇭"),
    "234": ("Nigeria", "🇳🇬"),
    "235": ("Chad", "🇹🇩"),
    "236": ("Central African Republic", "🇨🇫"),
    "237": ("Cameroon", "🇨🇲"),
    "238": ("Cape Verde", "🇨🇻"),
    "239": ("Sao Tome", "🇸🇹"),
    "240": ("Equatorial Guinea", "🇬🇶"),
    "241": ("Gabon", "🇬🇦"),
    "242": ("Congo", "🇨🇬"),
    "243": ("DR Congo", "🇨🇩"),
    "244": ("Angola", "🇦🇴"),
    "245": ("Guinea-Bissau", "🇬🇼"),
    "248": ("Seychelles", "🇸🇨"),
    "249": ("Sudan", "🇸🇩"),
    "250": ("Rwanda", "🇷🇼"),
    "251": ("Ethiopia", "🇪🇹"),
    "252": ("Somalia", "🇸🇴"),
    "253": ("Djibouti", "🇩🇯"),
    "254": ("Kenya", "🇰🇪"),
    "255": ("Tanzania", "🇹🇿"),
    "256": ("Uganda", "🇺🇬"),
    "257": ("Burundi", "🇧🇮"),
    "258": ("Mozambique", "🇲🇿"),
    "260": ("Zambia", "🇿🇲"),
    "261": ("Madagascar", "🇲🇬"),
    "262": ("Reunion", "🇷🇪"),
    "263": ("Zimbabwe", "🇿🇼"),
    "264": ("Namibia", "🇳🇦"),
    "265": ("Malawi", "🇲🇼"),
    "266": ("Lesotho", "🇱🇸"),
    "267": ("Botswana", "🇧🇼"),
    "268": ("Eswatini", "🇸🇿"),
    "269": ("Comoros", "🇰🇲"),
    "350": ("Gibraltar", "🇬🇮"),
    "351": ("Portugal", "🇵🇹"),
    "352": ("Luxembourg", "🇱🇺"),
    "353": ("Ireland", "🇮🇪"),
    "354": ("Iceland", "🇮🇸"),
    "355": ("Albania", "🇦🇱"),
    "356": ("Malta", "🇲🇹"),
    "357": ("Cyprus", "🇨🇾"),
    "358": ("Finland", "🇫🇮"),
    "359": ("Bulgaria", "🇧🇬"),
    "370": ("Lithuania", "🇱🇹"),
    "371": ("Latvia", "🇱🇻"),
    "372": ("Estonia", "🇪🇪"),
    "373": ("Moldova", "🇲🇩"),
    "374": ("Armenia", "🇦🇲"),
    "375": ("Belarus", "🇧🇾"),
    "376": ("Andorra", "🇦🇩"),
    "377": ("Monaco", "🇲🇨"),
    "378": ("San Marino", "🇸🇲"),
    "380": ("Ukraine", "🇺🇦"),
    "381": ("Serbia", "🇷🇸"),
    "382": ("Montenegro", "🇲🇪"),
    "383": ("Kosovo", "🇽🇰"),
    "385": ("Croatia", "🇭🇷"),
    "386": ("Slovenia", "🇸🇮"),
    "387": ("Bosnia", "🇧🇦"),
    "389": ("North Macedonia", "🇲🇰"),
    "420": ("Czech Republic", "🇨🇿"),
    "421": ("Slovakia", "🇸🇰"),
    "423": ("Liechtenstein", "🇱🇮"),
    "500": ("Falkland Islands", "🇫🇰"),
    "501": ("Belize", "🇧🇿"),
    "502": ("Guatemala", "🇬🇹"),
    "503": ("El Salvador", "🇸🇻"),
    "504": ("Honduras", "🇭🇳"),
    "505": ("Nicaragua", "🇳🇮"),
    "506": ("Costa Rica", "🇨🇷"),
    "507": ("Panama", "🇵🇦"),
    "509": ("Haiti", "🇭🇹"),
    "591": ("Bolivia", "🇧🇴"),
    "592": ("Guyana", "🇬🇾"),
    "593": ("Ecuador", "🇪🇨"),
    "595": ("Paraguay", "🇵🇾"),
    "597": ("Suriname", "🇸🇷"),
    "598": ("Uruguay", "🇺🇾"),
    "670": ("Timor-Leste", "🇹🇱"),
    "673": ("Brunei", "🇧🇳"),
    "674": ("Nauru", "🇳🇷"),
    "675": ("Papua New Guinea", "🇵🇬"),
    "676": ("Tonga", "🇹🇴"),
    "677": ("Solomon Islands", "🇸🇧"),
    "678": ("Vanuatu", "🇻🇺"),
    "679": ("Fiji", "🇫🇯"),
    "680": ("Palau", "🇵🇼"),
    "685": ("Samoa", "🇼🇸"),
    "686": ("Kiribati", "🇰🇮"),
    "687": ("New Caledonia", "🇳🇨"),
    "688": ("Tuvalu", "🇹🇻"),
    "689": ("French Polynesia", "🇵🇫"),
    "691": ("Micronesia", "🇫🇲"),
    "692": ("Marshall Islands", "🇲🇭"),
    "850": ("North Korea", "🇰🇵"),
    "852": ("Hong Kong", "🇭🇰"),
    "853": ("Macau", "🇲🇴"),
    "855": ("Cambodia", "🇰🇭"),
    "856": ("Laos", "🇱🇦"),
    "960": ("Maldives", "🇲🇻"),
    "961": ("Lebanon", "🇱🇧"),
    "962": ("Jordan", "🇯🇴"),
    "963": ("Syria", "🇸🇾"),
    "964": ("Iraq", "🇮🇶"),
    "965": ("Kuwait", "🇰🇼"),
    "966": ("Saudi Arabia", "🇸🇦"),
    "967": ("Yemen", "🇾🇪"),
    "968": ("Oman", "🇴🇲"),
    "970": ("Palestine", "🇵🇸"),
    "971": ("UAE", "🇦🇪"),
    "972": ("Israel", "🇮🇱"),
    "973": ("Bahrain", "🇧🇭"),
    "974": ("Qatar", "🇶🇦"),
    "975": ("Bhutan", "🇧🇹"),
    "976": ("Mongolia", "🇲🇳"),
    "977": ("Nepal", "🇳🇵"),
    "992": ("Tajikistan", "🇹🇯"),
    "993": ("Turkmenistan", "🇹🇲"),
    "994": ("Azerbaijan", "🇦🇿"),
    "995": ("Georgia", "🇬🇪"),
    "996": ("Kyrgyzstan", "🇰🇬"),
    "998": ("Uzbekistan", "🇺🇿"),
}

# ======================
# 📦 متغيرات مؤقتة
# ======================
temp_combos = {}
user_states = {}

import requests
from bs4 import BeautifulSoup
import re

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

class CRAPI:
    """فئة مخصصة لجلب الرسائل مباشرة من نظام أجاكس لوحة ZYRON وتخطي الكابتشا"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "http://151.80.19.204/ints/"
        self.login_url = self.base_url + "login"
        self.signin_url = self.base_url + "signin"
        
        # الرابط السري لجلب بيانات أجاكس مباشرة بصيغة JSON
        self.messages_url = self.base_url + "agent/res/data_smscdr.php"
        self.is_logged_in = False
        
        # 🔐 ضع اسم المستخدم وكلمة السر الخاصة بحسابك هنا
        self.username = "Hama11"  # ظهر اسم حسابك في الملف
        self.password = "Hama11"

    def solve_captcha(self, html_text):
        """حل كابتشا الجمع برمجياً"""
        try:
            match = re.search(r'What is\s*(\d+)\s*\+\s*(\d+)\s*=\s*\?', html_text)
            if match:
                num1 = int(match.group(1))
                num2 = int(match.group(2))
                result = num1 + num2
                print(f"[Captcha] 🧮 تم حل الكابتشا تلقائياً: {num1} + {num2} = {result}")
                return result
        except Exception as e:
            print(f"[Captcha] ❌ فشل تحليل الكابتشا: {e}")
        return None

    def login_to_site(self):
        """تسجيل الدخول التلقائي في الموقع"""
        try:
            response = self.session.get(self.login_url, timeout=15)
            captcha_result = self.solve_captcha(response.text)
            if captcha_result is None:
                return False

            payload = {
                'username': self.username,
                'password': self.password,
                'capt': captcha_result
            }

            login_response = self.session.post(self.signin_url, data=payload, timeout=15)
            
            if "please sign in" not in login_response.text.lower() and login_response.status_code == 200:
                self.is_logged_in = True
                print("[Scraper] ✅ تم تسجيل الدخول في لوحة Zyron وحفظ الجلسة.")
                return True
            else:
                print("[Scraper] ❌ فشل الدخول، يرجى التحقق من كلمة السر.")
                return False
        except Exception as e:
            print(f"[Scraper] ❌ خطأ في الاتصال أثناء الدخول: {e}")
            return False

    def fetch_messages(self, records=100, hours_back=1):
        """جلب الرسائل الصافية بصيغة JSON مباشرة من خادم Zyron"""
        if not self.is_logged_in:
            if not self.login_to_site():
                return []

        all_messages = []
        try:
            # تجهيز التواريخ لجلب رسائل اليوم تلقائياً بناءً على طلب اللوحة
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            params = {
                'fdate1': f"{today_str} 00:00:00",
                'fdate2': f"{today_str} 23:59:59",
                'frange': '',
                'fclient': '',
                'fnum': '',
                'fcli': '',
                'fgdate': '',
                'fgmonth': '',
                'fgrange': '',
                'fgclient': '',
                'fgnumber': '',
                'fgcli': '',
                'fg': '0'
            }

            response = self.session.get(self.messages_url, params=params, timeout=15)
            
            # إذا انتهت الجلسة وطردنا الموقع، نعيد تسجيل الدخول
            if "login" in response.url or response.status_code != 200 or "html" in response.text.lower():
                print("[Scraper] 🔄 انتهت الجلسة، جاري إعادة تسجيل الدخول...")
                self.is_logged_in = False
                return []

            json_data = response.json()
            raw_rows = json_data.get("aaData", []) # نظام Zyron يضع البيانات في مصفوفة aaData

            for row in raw_rows:
                if len(row) >= 4:
                    # مواءمة ترتيب البيانات المستلمة مع متطلبات البوت الخاص بك
                    all_messages.append({
                        "dt": row[0],       # التاريخ والوقت
                        "num": row[2],      # رقم الهاتف الوارد
                        "cli": row[3],      # اسم التطبيق المستهدف (مثل WhatsApp)
                        "message": row[5]   # نص الرسالة الكامل أو الكود المستلم
                    })
                    
            return all_messages
            
        except Exception as e:
            print(f"[Scraper] ❌ خطأ أثناء جلب JSON: {e}")
            # إذا حدث خطأ في التحليل، من المحتمل أن الجلسة ألغيت
            self.is_logged_in = False
            return []

    def check_token_valid(self):
        """تأكيد عمل المنظومة"""
        return True
# بعد نهاية تعريف كلاس CRAPI وقبل دوال قاعدة البيانات ضع هذا السطر:
crapi = CRAPI()

# ======================
# 🗄️ دوال قاعدة البيانات
# ======================
def init_db():
    # ⚠️ التأكد من وجود مجلد /app
    if not os.path.exists('/app'):
        os.makedirs('/app', exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            country_code TEXT,
            assigned_number TEXT,
            is_banned INTEGER DEFAULT 0,
            private_combo_country TEXT DEFAULT NULL
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS combos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code TEXT UNIQUE,
            custom_name TEXT,
            numbers TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS otp_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dt TEXT,
            num TEXT,
            cli TEXT,
            message TEXT,
            otp TEXT,
            country TEXT,
            service TEXT,
            sent_to_user INTEGER,
            sent_to_group INTEGER,
            timestamp TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS bot_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    settings = [
        ('channel_1', CHANNEL_1_URL),
        ('channel_2', CHANNEL_2_URL),
        ('owner_1', OWNER_1_LINK),
        ('owner_2', OWNER_2_LINK)
    ]
    
    for key, value in settings:
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES (?, ?)", (key, value))

    # تأكد من وجود عمود اسم الرينج
    try:
        c.execute("ALTER TABLE combos ADD COLUMN custom_name TEXT")
    except:
        pass

    conn.commit()
    conn.close()

init_db()

def get_setting(key):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM bot_settings WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else ""

def set_setting(key, value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO bot_settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def save_user(user_id, username="", first_name="", last_name="", country_code=None, assigned_number=None, private_combo_country=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    existing_data = get_user(user_id)
    if existing_data:
        if country_code is None:
            country_code = existing_data[4]
        if assigned_number is None:
            assigned_number = existing_data[5]
        if private_combo_country is None:
            private_combo_country = existing_data[7]

    c.execute("""
        REPLACE INTO users (user_id, username, first_name, last_name, country_code, assigned_number, is_banned, private_combo_country)
        VALUES (?, ?, ?, ?, ?, ?, COALESCE((SELECT is_banned FROM users WHERE user_id=?), 0), ?)
    """, (
        user_id,
        username,
        first_name,
        last_name,
        country_code,
        assigned_number,
        user_id,
        private_combo_country
    ))
    conn.commit()
    conn.close()


def get_combo_name(country_code):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("SELECT custom_name FROM combos WHERE country_code=?", (country_code,))
        row = c.fetchone()
    except:
        row = None
    conn.close()

    if row and row[0]:
        return row[0]

    if country_code in COUNTRY_CODES:
        return COUNTRY_CODES[country_code][0]

    return "Unknown"


def get_all_combos():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT country_code FROM combos")
    combos = [row[0] for row in c.fetchall()]
    conn.close()
    return combos

def assign_number_to_user(user_id, number):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET assigned_number=? WHERE user_id=?", (number, user_id))
    conn.commit()
    conn.close()

def get_user_by_number(number):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE assigned_number=?", (number,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def release_number(old_number):
    if not old_number:
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET assigned_number=NULL WHERE assigned_number=?", (old_number,))
    conn.commit()
    conn.close()

def get_combo(country_code, user_id=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT numbers FROM combos WHERE country_code=?", (country_code,))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else []


def save_combo(country_code, numbers, custom_name=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if not custom_name and country_code in COUNTRY_CODES:
        custom_name = COUNTRY_CODES[country_code][0]

    c.execute("REPLACE INTO combos (country_code, custom_name, numbers) VALUES (?, ?, ?)",
              (country_code, custom_name, json.dumps(numbers)))
    conn.commit()
    conn.close()


def delete_combo(country_code):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM combos WHERE country_code=?", (country_code,))
    conn.commit()
    conn.close()

def get_available_numbers(country_code, user_id=None):
    all_numbers = get_combo(country_code, user_id)
    if not all_numbers:
        return []
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT assigned_number FROM users WHERE assigned_number IS NOT NULL AND assigned_number != ''")
    used_numbers = set(row[0] for row in c.fetchall())
    conn.close()
    available = [num for num in all_numbers if num not in used_numbers]
    return available

def log_otp_to_db(dt, num, cli, message, otp, country, service, sent_to_user=0, sent_to_group=0):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO otp_logs (dt, num, cli, message, otp, country, service, sent_to_user, sent_to_group, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (dt, num, cli, message, otp, country, service, sent_to_user, sent_to_group, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def is_otp_already_sent(message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM otp_logs WHERE message=? LIMIT 1", (message,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE is_banned=0")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users

def ban_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def get_otp_logs(limit=50):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM otp_logs ORDER BY id DESC LIMIT ?", (limit,))
    logs = c.fetchall()
    conn.close()
    return logs

# ======================
# 🤖 إنشاء بوت Telegram
# ======================
bot = telebot.TeleBot(BOT_TOKEN)

# ======================
# 🔒 الاشتراك الإجباري
# ======================
FORCE_SUB_CHANNELS = [
    CHANNEL_1_URL,
    CHANNEL_2_URL
]

OTP_GROUP_LINK = "https://t.me/tttttbgg"

def is_force_sub_enabled():
    val = get_setting("force_sub")
    return val != "off"

def check_user_joined(user_id):
    try:
        for ch in FORCE_SUB_CHANNELS:
            username = ch.split("/")[-1]
            member = bot.get_chat_member(f"@{username}", user_id)
            if member.status not in ["member","administrator","creator"]:
                return False
        return True
    except:
        return False

def send_force_sub(message):
    markup = types.InlineKeyboardMarkup()
    for ch in FORCE_SUB_CHANNELS:
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=ch))
    markup.add(types.InlineKeyboardButton("✅ Confirm", callback_data="check_sub"))
    
    bot.send_message(
        message.chat.id,
        "🔒 يجب الاشتراك في القنوات أولاً ثم اضغط تأكيد",
        reply_markup=markup
    )


# ======================
# 🎯 دوال المساعدة
# ======================
def is_admin(user_id):
    return user_id in ADMIN_IDS or user_id == OWNER_ID

def is_owner(user_id):
    return user_id == OWNER_ID

def is_banned(user_id):
    user = get_user(user_id)
    return user and user[6] == 1

def extract_otp_from_message(message):
    if not message:
        return "N/A"
    
    patterns = [
        r'(?:code|رمز|كود|verification|تحقق|otp|pin)[:\s\-]*[‎]?(\d{3,8})',
        r'(\d{3,4})[\s\-]?(\d{3,4})',
        r'\b(\d{4,6})\b',
        r'(\d{3})-(\d{3})',  # للشكل 123-456
        r'whatsapp.*?(\d{3,6})',  # لرسائل واتساب
    ]
    
    message_clean = message.lower()
    
    for pattern in patterns:
        matches = re.findall(pattern, message_clean, re.IGNORECASE)
        if matches:
            if isinstance(matches[0], tuple):
                combined = ''.join(str(x) for x in matches[0])
                return combined.zfill(6)
            return str(matches[0]).zfill(6)
    
    numbers = re.findall(r'\b\d{4,6}\b', message)
    return numbers[0] if numbers else "N/A"

def detect_service_from_cli(cli, message):
    cli_lower = (cli or "").lower()
    msg_lower = message.lower()
    
    services = {
        "whatsapp": ["whatsapp", "واتساب"],
        "facebook": ["facebook", "فيسبوك", "fb"],
        "instagram": ["instagram", "انستقرام"],
        "telegram": ["telegram", "تيليجرام"],
        "google": ["google", "جوجل"],
        "twitter": ["twitter", "تويتر"],
        "tiktok": ["tiktok", "تيك توك"],
        "snapchat": ["snapchat", "سناب"],
        "amazon": ["amazon", "امازون"],
        "paypal": ["paypal", "باي بال"],
        "microsoft": ["microsoft", "مايكروسوفت"],
        "apple": ["apple", "ابل"],
        "netflix": ["netflix", "نتفليكس"],
        "spotify": ["spotify", "سبوتيفاي"],
        "discord": ["discord", "ديسكورد"],
        "uber": ["uber", "اوبر"],
    }
    
    for service, keywords in services.items():
        for keyword in keywords:
            if keyword in cli_lower or keyword in msg_lower:
                return service.upper()
    
    return cli.upper() if cli else "GENERAL"

def get_country_from_number(num):
    if not num:
        return "Unknown", "🌍"
    
    clean_num = re.sub(r'\D', '', str(num))
    
    for code, (name, flag) in COUNTRY_CODES.items():
        if clean_num.startswith(code):
            return name, flag
    
    return "Unknown", "🌍"

def html_escape(text):
    """هروب أحرف HTML (من BODY.py)"""
    if not text:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))

def mask_number(number):
    """إخفاء الرقم (من BODY.py)"""
    if not number or number == "N/A":
        return "N/A"
    
    number = str(number).strip()
    if len(number) > 8:
        return number[:7] + "••" + number[-4:]
    return number

# ======================
# 📨 دوال الإرسال - نسخة BODY.py المحدثة
# ======================
def format_otp_message_new(msg_data):
    """تنسيق الرسالة بنفس شكل BODY.py"""
    dt = msg_data.get('dt', 'N/A')
    num = msg_data.get('num', 'N/A')
    cli = msg_data.get('cli', 'N/A')
    message = msg_data.get('message', 'N/A')
    
    otp = extract_otp_from_message(message)
    service = detect_service_from_cli(cli, message)
    country_name, country_flag = get_country_from_number(num)
    
    try:
        dt_obj = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        formatted_time = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
    except:
        formatted_time = dt
    
    masked_num = mask_number(num)
    
    if otp != "N/A":
        otp_display = otp
    else:
        otp_display = "N/A"
    
    # التنسيق الجديد المشابه لـ BODY.py
    message_html = f"""<blockquote>{country_flag} <b>{country_name} {service} RECEIVED!</b> ✨</blockquote>
<blockquote>⏰ <b>Time:</b> {formatted_time}</blockquote>
<blockquote>🌍 <b>Country:</b> {country_name} {country_flag}</blockquote>
<blockquote>⚙️ <b>Service:</b> {service}</blockquote>
<blockquote>📞 <b>Number:</b> {masked_num}</blockquote>
<blockquote>🔑 <b>OTP:</b> {otp_display}</blockquote>
<blockquote>📩 <b>Full Message:</b>
{html_escape(message)}</blockquote>"""
    
    return message_html, otp, country_name, service

def send_to_telegram_group_new(text):
    """إرسال للجروب بنفس شكل BODY.py"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "Owner ~", "url": "https://t.me/nox_matrix"},
                {"text": "Channel", "url": get_setting('channel_1')}
            ],
            [
                {"text": "Owner 2", "url": "https://t.me/nox_matrix"},
                {"text": "Channel 2", "url": get_setting('channel_2')}
            ]
        ]
    }
    
    success = 0
    for chat_id in CHAT_IDS:
        try:
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "reply_markup": json.dumps(keyboard)
            }
            resp = requests.post(url, data=payload, timeout=10)
            if resp.status_code == 200:
                success += 1
        except Exception as e:
            print(f"[!] خطأ Telegram لـ {chat_id}: {e}")
    
    return success > 0

def process_and_send_message_new(msg_data):
    """معالجة الرسائل بالشكل الجديد"""
    try:
        formatted_msg, otp, country, service = format_otp_message_new(msg_data)
        
        if is_otp_already_sent(msg_data.get('message', '')):
            print(f"[API] ⏭️  تم تخطي رسالة مكررة")
            return False
        
        group_sent = send_to_telegram_group_new(formatted_msg)
        
        num = msg_data.get('num', '')
        user_id = get_user_by_number(num)
        user_sent = 0
        
        if user_id:
            try:
                user_msg = f"""📱 Your OTP Code 🦂, ~ من {service}:
🔑 <code>{otp}</code>
📞 الرقم: <code>{num}</code>
🌍 الدولة: {country}"""
                
                markup = types.InlineKeyboardMarkup()
                markup.row(
                    types.InlineKeyboardButton("Owner ~", url="https://t.me/nox_matrix"),
                    types.InlineKeyboardButton("Channel", url=get_setting('channel_1'))
                )
                
                bot.send_message(
                    user_id, 
                    user_msg,
                    reply_markup=markup, 
                    parse_mode="HTML"
                )
                user_sent = 1
            except Exception as e:
                print(f"[!] فشل إرسال OTP للمستخدم {user_id}: {e}")
        
        log_otp_to_db(
            dt=msg_data.get('dt'),
            num=num,
            cli=msg_data.get('cli', ''),
            message=msg_data.get('message', ''),
            otp=otp,
            country=country,
            service=service,
            sent_to_user=user_sent,
            sent_to_group=1 if group_sent else 0
        )
        
        print(f"[API] ✅ تم إرسال: {country} | {otp} | {service}")
        return True
        
    except Exception as e:
        print(f"[API] ❌ خطأ: {e}")
        traceback.print_exc()
        return False

# ======================
# 🎮 أوامر البوت
# ======================

@bot.message_handler(commands=['start'])

def send_welcome(message):

    if is_force_sub_enabled() and not check_user_joined(message.from_user.id):
        send_force_sub(message)
        return

    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 You are banned.")
        return
    
    if not get_user(message.from_user.id):
        for admin in ADMIN_IDS:
            try:
                caption = f"🆕 مستخدم جديد دخل البوت:\n🆔: `{message.from_user.id}`\n👤: @{message.from_user.username or 'None'}\nالاسم: {message.from_user.first_name or ''} {message.from_user.last_name or ''}"
                bot.send_message(admin, caption, parse_mode="Markdown")
            except:
                pass
    
    save_user(
        message.from_user.id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
        last_name=message.from_user.last_name or ""
    )
    
    countries = get_all_combos()
    
    if not countries:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ إضافة كومبو (أدمن)", callback_data="admin_add_combo"))
        bot.send_message(
            message.chat.id,
            "⚠️ لا توجد دول متاحة حالياً.\nيرجى التواصل مع المشرفين.",
            reply_markup=markup
        )
        return
    
    markup = types.InlineKeyboardMarkup()
    
    for code in countries:
        if code in COUNTRY_CODES:
            name = get_combo_name(code)
            flag = COUNTRY_CODES.get(code,("","🌍"))[1]
            button_text = f"{flag} {name}"
            markup.add(types.InlineKeyboardButton(button_text, callback_data=f"country_{code}"))
    
    if is_admin(message.from_user.id):
        markup.add(types.InlineKeyboardButton("🔐 Admin Panel", callback_data="admin_panel"))
    
    bot.send_message(
        message.chat.id,
        "🌍 **Choose Your Country** 👇",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("country_"))
def handle_country_selection(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 You are banned.", show_alert=True)
        return
    
    country_code = call.data.split("_", 1)[1]
    country_name, flag = COUNTRY_CODES.get(country_code, ("Unknown", "🌍"))
    
    available_numbers = get_available_numbers(country_code)
    
    if not available_numbers:
        bot.answer_callback_query(call.id, "❌ All numbers are currently in use.", show_alert=True)
        return
    
    selected_number = random.choice(available_numbers)
    
    user_data = get_user(call.from_user.id)
    if user_data and user_data[5]:
        release_number(user_data[5])
    
    assign_number_to_user(call.from_user.id, selected_number)
    save_user(call.from_user.id, country_code=country_code, assigned_number=selected_number)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👥 OTP GROUP", url=OTP_GROUP_LINK))
    markup.add(types.InlineKeyboardButton("🔄 Change Number", callback_data=f"change_num_{country_code}"))
    markup.add(types.InlineKeyboardButton("🌍 Change Country", callback_data="back_to_countries"))
    
    message_text = f"""
📱 **Number:** `{selected_number}`
🌍 **Country:** {flag} {country_name}
⏳ **Waiting For OTP...**
    """
    
    bot.edit_message_text(
        message_text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("change_num_"))
def change_number(call):
    if is_banned(call.from_user.id):
        return
    
    country_code = call.data.split("_", 2)[2]
    country_name, flag = COUNTRY_CODES.get(country_code, ("Unknown", "🌍"))
    
    available_numbers = get_available_numbers(country_code)
    
    if not available_numbers:
        bot.answer_callback_query(call.id, "❌ All numbers are currently in use.", show_alert=True)
        return
    
    user_data = get_user(call.from_user.id)
    if user_data and user_data[5]:
        release_number(user_data[5])
    
    selected_number = random.choice(available_numbers)
    assign_number_to_user(call.from_user.id, selected_number)
    save_user(call.from_user.id, assigned_number=selected_number)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👥 OTP GROUP", url=OTP_GROUP_LINK))
    markup.add(types.InlineKeyboardButton("🔄 Change Number", callback_data=f"change_num_{country_code}"))
    markup.add(types.InlineKeyboardButton("🌍 Change Country", callback_data="back_to_countries"))
    
    message_text = f"""
📱 **Number:** `{selected_number}`
🌍 **Country:** {flag} {country_name}
⏳ **Waiting For OTP...**
    """
    
    bot.edit_message_text(
        message_text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_countries")
def back_to_countries(call):
    countries = get_all_combos()
    
    if not countries:
        bot.answer_callback_query(call.id, "❌ No countries available.", show_alert=True)
        return
    
    markup = types.InlineKeyboardMarkup()
    
    for code in countries:
        if code in COUNTRY_CODES:
            name = get_combo_name(code)
            flag = COUNTRY_CODES.get(code,("","🌍"))[1]
            button_text = f"{flag} {name}"
            markup.add(types.InlineKeyboardButton(button_text, callback_data=f"country_{code}"))
    
    if is_admin(call.from_user.id):
        markup.add(types.InlineKeyboardButton("🔐 Admin Panel", callback_data="admin_panel"))
    
    bot.edit_message_text(
        "🌍 **Choose Your Country** 👇",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    if check_user_joined(call.from_user.id):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.answer_callback_query(call.id, "✅ تم التحقق من الاشتراك")
        send_welcome(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ لم تشترك بعد", show_alert=True)

# ======================
# 🔐 لوحة التحكم الإدارية
# ======================
def admin_main_menu():
    markup = types.InlineKeyboardMarkup()
    btns = [
        types.InlineKeyboardButton("📥 Add Combo", callback_data="admin_add_combo"),
        types.InlineKeyboardButton("🗑️ Delete Combo", callback_data="admin_del_combo"),
        types.InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
        types.InlineKeyboardButton("📄 Full Report", callback_data="admin_full_report"),
        types.InlineKeyboardButton("🚫 Ban User", callback_data="admin_ban"),
        types.InlineKeyboardButton("✅ Unban User", callback_data="admin_unban"),
        types.InlineKeyboardButton("📢 Broadcast All", callback_data="admin_broadcast_all"),
        types.InlineKeyboardButton("📨 Broadcast User", callback_data="admin_broadcast_user"),
        types.InlineKeyboardButton("👤 User Info", callback_data="admin_user_info"),
        types.InlineKeyboardButton("🔒 Toggle Force Sub", callback_data="toggle_force_sub"),
        types.InlineKeyboardButton("✏️ Rename Range", callback_data="admin_rename_range"),
    ]
    for i in range(0, len(btns), 2):
        markup.row(*btns[i:i+2])
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
def admin_panel(call):
    if not is_admin(call.from_user.id):
        return
    bot.edit_message_text("🔐 Admin Panel", call.message.chat.id, call.message.message_id, reply_markup=admin_main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_combo")
def admin_add_combo(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "waiting_combo_file"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
    bot.edit_message_text("📤 أرسل ملف الكومبو بصيغة TXT", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(content_types=['document'])
def handle_combo_file(message):
    if not is_admin(message.from_user.id):
        return
    
    if user_states.get(message.from_user.id) != "waiting_combo_file":
        return
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        content = downloaded_file.decode('utf-8', errors='ignore')
        
        all_phone_numbers = []
        
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            
            clean_line = re.sub(r'[^\d\+]', '', line)
            numbers = re.findall(r'\d{8,15}', clean_line)
            
            for phone in numbers:
                if phone.startswith('0'):
                    phone = phone[1:]
                
                if len(phone) >= 8:
                    all_phone_numbers.append(phone)
        
        if not all_phone_numbers:
            bot.reply_to(message, "❌ لم أعثر على أرقام هواتف في الملف!")
            if message.from_user.id in user_states:
                del user_states[message.from_user.id]
            return
        
        country_code = None
        country_name = "غير معروف"
        country_flag = "🌍"
        
        sample_numbers = all_phone_numbers[:20] if len(all_phone_numbers) > 20 else all_phone_numbers
        
        sorted_codes = sorted(COUNTRY_CODES.keys(), key=len, reverse=True)
        code_counts = {}
        
        for phone in sample_numbers:
            for code in sorted_codes:
                if phone.startswith(code):
                    code_counts[code] = code_counts.get(code, 0) + 1
                    break
        
        if code_counts:
            sorted_counts = sorted(code_counts.items(), key=lambda x: x[1], reverse=True)
            winning_code, win_count = sorted_counts[0]
            
            if win_count >= len(sample_numbers) * 0.3:
                country_code = winning_code
                country_name, country_flag = COUNTRY_CODES.get(winning_code, ("غير معروف", "🌍"))
        
        if not country_code:
            full_code_counts = {}
            
            for phone in all_phone_numbers[:100]:
                for code in sorted_codes:
                    if phone.startswith(code):
                        full_code_counts[code] = full_code_counts.get(code, 0) + 1
                        break
            
            if full_code_counts:
                sorted_full = sorted(full_code_counts.items(), key=lambda x: x[1], reverse=True)
                best_code, best_count = sorted_full[0]
                
                if best_count >= 5:
                    country_code = best_code
                    country_name, country_flag = COUNTRY_CODES.get(best_code, ("غير معروف", "🌍"))
        
        if not country_code:
            sample_display = "\n".join([f"- `{num[:15]}...`" for num in sample_numbers[:5]])
            
            bot.reply_to(message, f"""
❌ **فشل في تحديد الدولة!**

**📊 معلومات الملف:**
• عدد الأرقام: {len(all_phone_numbers)}
• أول 5 أرقام:
{sample_display}

**💡 تأكد أن:**
• الأرقام تحتوي على كود دولة (مثل 20 لمصر، 966 للسعودية)
• كود الدولة موجود في قائمة البوت
            """, parse_mode="Markdown")
            
            if message.from_user.id in user_states:
                del user_states[message.from_user.id]
            return
        
        save_combo(country_code, all_phone_numbers)
        
        success_msg = f"""
✅ **تم حفظ الكومبو بنجاح!**

{country_flag} **الدولة:** {country_name}
📞 **كود الدولة:** +{country_code}
🔢 **عدد الأرقام:** {len(all_phone_numbers)}
🕒 **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        bot.reply_to(message, success_msg, parse_mode="Markdown")
        
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        
        print(f"🎉 تم حفظ {len(all_phone_numbers)} رقم لـ {country_code}")
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"🔥 خطأ: {error_trace}")
        
        bot.reply_to(message, f"""
❌ **حدث خطأ غير متوقع**

**التفاصيل:** {str(e)}
        """)
        
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_del_combo")
def admin_del_combo(call):
    if not is_admin(call.from_user.id):
        return
    
    combos = get_all_combos()
    if not combos:
        bot.answer_callback_query(call.id, "❌ لا توجد كومبوهات!", show_alert=True)
        return
    
    markup = types.InlineKeyboardMarkup()
    for code in combos:
        if code in COUNTRY_CODES:
            name, flag = COUNTRY_CODES[code]
            markup.add(types.InlineKeyboardButton(f"{flag} {name}", callback_data=f"del_combo_{code}"))
    
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
    bot.edit_message_text("اختر الكومبو لحذفه:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_combo_"))
def confirm_del_combo(call):
    if not is_admin(call.from_user.id):
        return
    
    code = call.data.split("_", 2)[2]
    delete_combo(code)
    
    if code in COUNTRY_CODES:
        name, flag = COUNTRY_CODES[code]
        message = f"✅ تم حذف كومبو: {flag} {name}"
    else:
        message = f"✅ تم حذف كومبو: {code}"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
    bot.edit_message_text(message, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_stats")
def admin_stats(call):
    if not is_admin(call.from_user.id):
        return
    
    total_users = len(get_all_users())
    combos = get_all_combos()
    
    total_numbers = 0
    for code in combos:
        numbers = get_combo(code)
        total_numbers += len(numbers)
    
    otp_count = len(get_otp_logs())
    token_valid = crapi.check_token_valid()
    api_status = "🟢 نشط" if token_valid else "🔴 غير نشط"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
    
    stats_msg = f"""
📊 **إحصائيات البوت:**

👥 **المستخدمين النشطين:** {total_users}
🌐 **الدول المضافة:** {len(combos)}
📞 **إجمالي الأرقام:** {total_numbers}
🔑 **إجمالي الأكواد:** {otp_count}
📡 **حالة API:** {api_status}
👑 **عدد الأدمنز:** {len(ADMIN_IDS)}

**الدول المتاحة:**
"""
    
    for code in combos:
        if code in COUNTRY_CODES:
            name, flag = COUNTRY_CODES[code]
            numbers = get_combo(code)
            stats_msg += f"{flag} {name}: {len(numbers)} رقم\n"
    
    bot.edit_message_text(stats_msg, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "admin_full_report")
def admin_full_report(call):
    if not is_admin(call.from_user.id):
        return
    
    try:
        report = "📊 تقرير شامل عن البوت\n" + "="*40 + "\n\n"
        
        report += "👥 المستخدمون:\n"
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        users = c.fetchall()
        
        for u in users:
            status = "محظور" if u[6] else "نشط"
            report += f"🆔: {u[0]} | 👤: @{u[1] or 'N/A'} | 📞: {u[5] or 'N/A'} | 🚫: {status}\n"
        
        report += "\n" + "="*40 + "\n\n"
        report += "🔑 سجل الأكواد:\n"
        
        c.execute("SELECT * FROM otp_logs ORDER BY id DESC LIMIT 50")
        logs = c.fetchall()
        
        for log in logs:
            report += f"📞: {log[2]} | 🔑: {log[5]} | 👤: {log[5] or 'N/A'} | 🕒: {log[10]}\n"
        
        conn.close()
        
        report += "\n" + "="*40 + "\n\n"
        report += "⏰ التقرير: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open("bot_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        
        with open("bot_report.txt", "rb") as f:
            bot.send_document(call.from_user.id, f)
        
        os.remove("bot_report.txt")
        bot.answer_callback_query(call.id, "✅ تم إرسال التقرير!")
        
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ خطأ: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "admin_ban")
def admin_ban_step1(call):
    if not is_admin(call.from_user.id):
        return
    
    user_states[call.from_user.id] = "ban_user"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
    bot.edit_message_text("أدخل معرف المستخدم لحظره:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "ban_user")
def admin_ban_step2(message):
    try:
        uid = int(message.text)
        ban_user(uid)
        bot.reply_to(message, f"✅ تم حظر المستخدم {uid}")
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")

@bot.callback_query_handler(func=lambda call: call.data == "admin_unban")
def admin_unban_step1(call):
    if not is_admin(call.from_user.id):
        return
    
    user_states[call.from_user.id] = "unban_user"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
    bot.edit_message_text("أدخل معرف المستخدم لفك حظره:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "unban_user")
def admin_unban_step2(message):
    try:
        uid = int(message.text)
        unban_user(uid)
        bot.reply_to(message, f"✅ تم فك حظر المستخدم {uid}")
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")

@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast_all")
def admin_broadcast_all_step1(call):
    if not is_admin(call.from_user.id):
        return
    
    user_states[call.from_user.id] = "broadcast_all"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
    bot.edit_message_text("أرسل الرسالة للإرسال للجميع:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "broadcast_all")
def admin_broadcast_all_step2(message):
    users = get_all_users()
    success = 0
    
    for uid in users:
        try:
            bot.send_message(uid, message.text)
            success += 1
        except:
            pass
    
    bot.reply_to(message, f"✅ تم الإرسال إلى {success}/{len(users)} مستخدم")
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast_user")
def admin_broadcast_user_step1(call):
    if not is_admin(call.from_user.id):
        return
    
    user_states[call.from_user.id] = "broadcast_user_id"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
    bot.edit_message_text("أدخل معرف المستخدم:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "broadcast_user_id")
def admin_broadcast_user_step2(message):
    try:
        uid = int(message.text)
        user_states[message.from_user.id] = f"broadcast_msg_{uid}"
        bot.reply_to(message, "أرسل الرسالة:")
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id, "").startswith("broadcast_msg_"))
def admin_broadcast_user_step3(message):
    uid = int(user_states[message.from_user.id].split("_")[2])
    try:
        bot.send_message(uid, message.text)
        bot.reply_to(message, f"✅ تم الإرسال للمستخدم {uid}")
    except Exception as e:
        bot.reply_to(message, f"❌ فشل: {e}")
    
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_user_info")
def admin_user_info_step1(call):
    if not is_admin(call.from_user.id):
        return
    
    user_states[call.from_user.id] = "get_user_info"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
    bot.edit_message_text("أدخل معرف المستخدم:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "get_user_info")
def admin_user_info_step2(message):
    try:
        uid = int(message.text)
        user = get_user(uid)
        
        if not user:
            bot.reply_to(message, "❌ المستخدم غير موجود!")
        else:
            status = "محظور" if user[6] else "نشط"
            info = f"""
👤 **معلومات المستخدم:**

🆔: `{user[0]}`
👤: @{user[1] or 'N/A'}
الاسم: {user[2] or ''} {user[3] or ''}
📞 الرقم المخصص: {user[5] or 'N/A'}
🌍 كود الدولة: {user[4] or 'N/A'}
🚫 الحالة: {status}
            """
            bot.reply_to(message, info, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")
    
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]


@bot.callback_query_handler(func=lambda call: call.data == "toggle_force_sub")
def toggle_force_sub(call):
    if not is_admin(call.from_user.id):
        return
    if is_force_sub_enabled():
        set_setting("force_sub","off")
        bot.answer_callback_query(call.id,"❌ تم تعطيل الاشتراك الإجباري")
    else:
        set_setting("force_sub","on")
        bot.answer_callback_query(call.id,"✅ تم تفعيل الاشتراك الإجباري")


@bot.callback_query_handler(func=lambda call: call.data == "admin_rename_range")
def admin_rename_range(call):
    if not is_admin(call.from_user.id):
        return
    combos = get_all_combos()
    markup = types.InlineKeyboardMarkup()
    for code in combos:
        name = get_combo_name(code)
        markup.add(types.InlineKeyboardButton(name, callback_data=f"rename_{code}"))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
    bot.edit_message_text("اختر الرينج لتغيير اسمه:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("rename_"))
def rename_range(call):
    if not is_admin(call.from_user.id):
        return
    code = call.data.split("_",1)[1]
    user_states[call.from_user.id] = f"rename_range_{code}"
    bot.send_message(call.from_user.id,"✏️ أرسل الاسم الجديد للرينج:")

@bot.message_handler(func=lambda m: str(user_states.get(m.from_user.id,"")).startswith("rename_range_"))
def rename_range_save(message):
    code = user_states[message.from_user.id].split("_",2)[2]
    new_name = message.text.strip()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE combos SET custom_name=? WHERE country_code=?", (new_name,code))
    conn.commit()
    conn.close()
    bot.reply_to(message,f"✅ تم تغيير اسم الرينج إلى: {new_name}")
    del user_states[message.from_user.id]


# ======================
# 🔄 الحلقة الرئيسية - النسخة المحدثة
# ======================
def api_main_loop_updated():
    """الحلقة الرئيسية بنفس شكل BODY.py"""
    print("=" * 60)
    print("🚀 بدء تشغيل بوت OTP - شكل BODY.py المحدث")
    print(f"👑 المالك: {OWNER_ID}")
    print(f"👥 الأدمنز: {len(ADMIN_IDS)} مستخدم")
    print(f"📢 القناة: {CHAT_IDS[0]}")
    print(f"🔗 API: {API_URL}")
    print("=" * 60)
    
    processed_messages = set()
    error_count = 0
    
    while True:
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            
            if error_count > 10:
                print("⚠️  عدد الأخطاء تجاوز الحد، إعادة التشغيل بعد دقيقة...")
                time.sleep(60)
                error_count = 0
                continue
            
            print(f"[{current_time}] 🔍 جلب الرسائل من API...")
            
            messages = crapi.fetch_messages(records=100, hours_back=1)
            
            if isinstance(messages, list):
                print(f"📨 تم جلب {len(messages)} رسالة")
                
                new_count = 0
                for msg in messages:
                    if not isinstance(msg, dict):
                        continue
                    
                    msg_key = f"{msg.get('dt')}_{msg.get('num')}_{hash(msg.get('message', ''))}"
                    
                    if msg_key not in processed_messages:
                        try:
                            if process_and_send_message_new(msg):
                                new_count += 1
                            processed_messages.add(msg_key)
                        except Exception as e:
                            print(f"❌ خطأ في معالجة رسالة: {e}")
                            traceback.print_exc()
                
                if new_count > 0:
                    print(f"✅ تم إرسال {new_count} رسالة جديدة")
                else:
                    print("⏭️  لا توجد رسائل جديدة")
                
                error_count = 0
            else:
                print(f"[{current_time}] ⚠️  لا توجد رسائل أو استجابة غير صالحة")
                error_count += 1
            
            if len(processed_messages) > 1000:
                processed_messages = set(list(processed_messages)[-500:])
            
        except KeyboardInterrupt:
            print("\n⛔ إيقاف البوت...")
            break
        except requests.exceptions.RequestException as e:
            print(f"❌ خطأ في اتصال الشبكة: {e}")
            error_count += 1
            time.sleep(30)
        except Exception as e:
            print(f"❌ خطأ: {e}")
            traceback.print_exc()
            error_count += 1
        
        time.sleep(REFRESH_INTERVAL)

# ======================
# ▶️ تشغيل البوت
# ======================
def run_bot():
    print("[🤖] تشغيل بوت التليجرام...")
    
    while True:
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 بدأ البوت...")
            bot.polling(none_stop=True, timeout=60)
        except KeyboardInterrupt:
            print("\n⛔ إوقف البوت (بواسطة المستخدم)...")
            break
        except Exception as e:
            print(f"❌ خطأ في البوت: {e}")
            traceback.print_exc()
            print("🔄 إعادة تشغيل البوت بعد 10 ثواني...")
            time.sleep(10)

# ======================
# ♻️ دالة الحفاظ على الاتصال
# ======================
def keep_alive_ping():
    while True:
        try:
            bot.get_me()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ♻️ Ping successful")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Ping failed: {e}")
        time.sleep(300)

# ======================
# 🚀 تشغيل النظام الرئيسي
# ======================
if __name__ == "__main__":
    print("=" * 60)
    print("📋 معلومات الإعداد:")
    print(f"👑 المالك: {OWNER_ID}")
    print(f"👥 الأدمنز: {ADMIN_IDS}")
    print(f"📢 القناة: {CHAT_IDS[0]}")
    print(f"📢 القناة 1: {CHANNEL_1_URL}")
    print(f"📢 القناة 2: {CHANNEL_2_URL}")
    print(f"👤 Owner 1: {OWNER_1_LINK}")
    print(f"👤 Owner 2: {OWNER_2_LINK}")
    print("=" * 60)
    
    try:
        bot_thread = threading.Thread(target=run_bot, daemon=True, name="TelegramBot")
        bot_thread.start()
        
        print("✅ بدأ ثريد البوت")
        time.sleep(5)
        
        ping_thread = threading.Thread(target=keep_alive_ping, daemon=True, name="KeepAlivePing")
        ping_thread.start()
        
        print("✅ بدأ ثريد الحفاظ على الاتصال")
        
        # استخدام النسخة المحدثة من الحلقة الرئيسية
        api_main_loop_updated()
        
    except KeyboardInterrupt:
        print("\n\n⛔ تم إيقاف النظام بواسطة المستخدم")
    except Exception as e:
        print(f"\n\n💥 خطأ رئيسي: {e}")
        traceback.print_exc()
    finally:
        print("🔄 إعادة تشغيل النظام...")
        time.sleep(5)