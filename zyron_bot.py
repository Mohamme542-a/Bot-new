# -*- coding: utf-8 -*-
"""
====================================================
  ZYRON SMS Telegram Bot — نسخة كاملة متكاملة
  موقع: http://151.80.19.204/ints/
====================================================
التثبيت:
  pip install pyTelegramBotAPI requests beautifulsoup4
التشغيل:
  python zyron_bot.py
"""

import os
import re
import json
import time
import random
import sqlite3
import threading
import traceback
from datetime import datetime

import requests
import telebot
from telebot import types

# ======================================================
# 🔐 إعدادات الموقع (ZYRON SMS Panel)
# ======================================================
SITE_BASE_URL = "http://151.80.19.204/ints/"
SITE_USERNAME = "Hama11"         # ← غيّر اسم المستخدم
SITE_PASSWORD = "Hama11"         # ← غيّر كلمة المرور

# ======================================================
# 🤖 إعدادات البوت
# ======================================================
BOT_TOKEN        = "8794957674:AAHFqCRjwc19Kr54BLFpqEQ2NsPibEAt-_w"
GROUP_CHAT_IDS   = ["-1003921031641"]   # القناة/الجروب العام لنشر OTP
OWNER_ID         = 8761832730
ADMIN_IDS        = [8761832730]
DB_PATH          = "zyron_bot.db"
REFRESH_INTERVAL = 5                    # ثواني بين كل عملية جلب

# ======================================================
# 🔗 القنوات والروابط
# ======================================================
CHANNEL_1_URL = "https://t.me/gvbhvc669"
CHANNEL_2_URL = "https://t.me/fhbcf5888"
OWNER_1_LINK  = "https://t.me/nox_matrix"
OWNER_2_LINK  = "https://t.me/nox_matrix"
OTP_GROUP_LINK = "https://t.me/+IaUh8c8vXnIzYTM0"
FORCE_SUB_CHANNELS = [CHANNEL_1_URL, CHANNEL_2_URL]

# ======================================================
# 🗺️ أكواد الدول (مختصرة - يمكن إضافة المزيد)
# ======================================================
            # ======================================================
# 📦 قاموس أكواد الدول والدول والرموز التعبيرية الشامل
# ======================================================
COUNTRY_CODES = {
    "1":   ("USA/Canada", "🇺🇸"), "7":   ("Russia/KZ", "🇷🇺"),
    "20":  ("Egypt", "🇪🇬"),     "27":  ("South Africa", "🇿🇦"),
    "30":  ("Greece", "🇬🇷"),    "31":  ("Netherlands", "🇳🇱"),
    "32":  ("Belgium", "🇧🇪"),   "33":  ("France", "🇫🇷"),
    "34":  ("Spain", "🇪🇸"),     "36":  ("Hungary", "🇭🇺"),
    "39":  ("Italy", "🇮🇹"),     "40":  ("Romania", "🇷🇴"),
    "41":  ("Switzerland", "🇨🇭"),"43": ("Austria", "🇦🇹"),
    "44":  ("UK", "🇬🇧"),        "45":  ("Denmark", "🇩🇰"),
    "46":  ("Sweden", "🇸🇪"),    "47":  ("Norway", "🇳🇴"),
    "48":  ("Poland", "🇵🇱"),    "49":  ("Germany", "🇩🇪"),
    "52":  ("Mexico", "🇲🇽"),    "55":  ("Brazil", "🇧🇷"),
    "60":  ("Malaysia", "🇲🇾"),  "61":  ("Australia", "🇦🇺"),
    "62":  ("Indonesia", "🇮🇩"), "63":  ("Philippines", "🇵🇭"),
    "65":  ("Singapore", "🇸🇬"), "66":  ("Thailand", "🇹🇭"),
    "81":  ("Japan", "🇯🇵"),     "82":  ("Korea", "🇰🇷"),
    "84":  ("Vietnam", "🇻🇳"),   "86":  ("China", "🇨🇳"),
    "90":  ("Turkey", "🇹🇷"),    "91":  ("India", "🇮🇳"),
    "92":  ("Pakistan", "🇵🇰"),  "212": ("Morocco", "🇲🇦"),
    "213": ("Algeria", "🇩🇿"),   "216": ("Tunisia", "🇹🇳"),
    "218": ("Libya", "🇱🇾"),     "234": ("Nigeria", "🇳🇬"),
    "236": ("Central African", "🇨🇫"),
    "249": ("Sudan", "🇸🇩"),     "351": ("Portugal", "🇵🇹"),
    "352": ("Luxembourg", "🇱🇺"),"353": ("Ireland", "🇮🇪"),
    "358": ("Finland", "🇫🇮"),   "359": ("Bulgaria", "🇧🇬"),
    "380": ("Ukraine", "🇺🇦"),   "420": ("Czech", "🇨🇿"),
    "421": ("Slovakia", "🇸🇰"),  "880": ("Bangladesh", "🇧🇩"),
    "961": ("Lebanon", "🇱🇧"),   "962": ("Jordan", "🇯🇴"),
    "963": ("Syria", "🇸🇾"),     "964": ("Iraq", "🇮🇶"),
    "965": ("Kuwait", "🇰🇼"),    "966": ("Saudi Arabia", "🇸🇦"),
    "967": ("Yemen", "🇾🇪"),     "968": ("Oman", "🇴🇲"),
    "970": ("Palestine", "🇵🇸"), "971": ("UAE", "🇦🇪"),
    "972": ("Israel", "🇮🇱"),    "973": ("Bahrain", "🇧🇭"),
    "974": ("Qatar", "🇶🇦"),     "994": ("Azerbaijan", "🇦🇿"),
    "995": ("Georgia", "🇬🇪"),   "998": ("Uzbekistan", "🇺🇿"),

# ======================================================
# 📦 حالة مؤقتة
# ======================================================
user_states = {}

# ======================================================
# 🌐 CRAPI - جالب الرسائل من لوحة ZYRON
# ======================================================
class ZyronAPI:
    """جلب الرسائل من لوحة ZYRON SMS عن طريق Ajax + تخطي الكابتشا الحسابي"""

    def __init__(self):
        self.session = requests.Session()
        self.base_url    = SITE_BASE_URL.rstrip("/") + "/"
        self.login_url   = self.base_url + "login"
        self.signin_url  = self.base_url + "signin"
        self.stats_page  = self.base_url + "agent/SMSCDRStats"
        self.ajax_url    = self.base_url + "agent/res/data_smscdr.php"
        self.is_logged_in = False

        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        })

    def _solve_captcha(self, html_text):
        try:
            m = re.search(r"What\s+is\s*(\d+)\s*\+\s*(\d+)\s*=", html_text, re.I)
            if m:
                return int(m.group(1)) + int(m.group(2))
        except Exception:
            pass
        return None

    def login(self):
        try:
            r = self.session.get(self.login_url, timeout=20)
            answer = self._solve_captcha(r.text)
            if answer is None:
                print("[Zyron] ❌ لم أجد سؤال الكابتشا")
                return False

            payload = {
                "username": SITE_USERNAME,
                "password": SITE_PASSWORD,
                "capt": str(answer),
            }
            r2 = self.session.post(
                self.signin_url, data=payload, timeout=20,
                headers={"Referer": self.login_url},
                allow_redirects=True,
            )

            txt = r2.text.lower()
            ok = (
                r2.status_code == 200
                and "please sign in" not in txt
                and "invalid" not in txt
            )
            self.is_logged_in = ok
            if ok:
                print("[Zyron] ✅ تم تسجيل الدخول بنجاح.")
            else:
                print("[Zyron] ❌ فشل تسجيل الدخول.")
            return ok
        except Exception as e:
            print(f"[Zyron] ❌ خطأ في تسجيل الدخول: {e}")
            return False

    def fetch_messages(self):
        if not self.is_logged_in and not self.login():
            return []

        today = datetime.now().strftime("%Y-%m-%d")
        params = {
            "fdate1": f"{today} 00:00:00",
            "fdate2": f"{today} 23:59:59",
            "frange": "", "fclient": "", "fnum": "", "fcli": "",
            "fgdate": "", "fgmonth": "", "fgrange": "",
            "fgclient": "", "fgnumber": "", "fgcli": "", "fg": "0",
        }
        headers = {
            "Referer": self.stats_page,
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }

        try:
            r = self.session.get(self.ajax_url, params=params,
                                 headers=headers, timeout=20,
                                 allow_redirects=False)

            # ٣٠٢ يعني انتهت الجلسة
            if r.status_code in (301, 302) or "login" in r.url:
                print("[Zyron] 🔄 انتهت الجلسة... إعادة دخول")
                self.is_logged_in = False
                return []

            if "Direct Script Access" in r.text or r.status_code != 200:
                self.is_logged_in = False
                return []

            data = r.json()
            rows = data.get("aaData", [])
            out = []
            for row in rows:
                if len(row) >= 6:
                    out.append({
                        "dt":      str(row[0]),
                        "range":   str(row[1]) if len(row) > 1 else "",
                        "num":     str(row[2]),
                        "cli":     str(row[3]),
                        "client":  str(row[4]) if len(row) > 4 else "",
                        "message": str(row[5]),
                    })
            return out
        except Exception as e:
            print(f"[Zyron] ❌ خطأ في الجلب: {e}")
            self.is_logged_in = False
            return []


zyron = ZyronAPI()

# ======================================================
# 🗄️ قاعدة البيانات
# ======================================================
def db():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = db(); c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        user_id           INTEGER PRIMARY KEY,
        username          TEXT,
        first_name        TEXT,
        last_name         TEXT,
        country_code      TEXT,
        assigned_number   TEXT,
        is_banned         INTEGER DEFAULT 0,
        join_date         TEXT
    );
    CREATE TABLE IF NOT EXISTS combos (
        country_code  TEXT PRIMARY KEY,
        custom_name   TEXT,
        numbers       TEXT
    );
    CREATE TABLE IF NOT EXISTS otp_logs (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        dt           TEXT,
        num          TEXT,
        cli          TEXT,
        message      TEXT,
        otp          TEXT,
        country      TEXT,
        service      TEXT,
        sent_to_user INTEGER DEFAULT 0,
        sent_to_group INTEGER DEFAULT 0,
        timestamp    TEXT
    );
    CREATE TABLE IF NOT EXISTS sent_hashes (
        h         TEXT PRIMARY KEY,
        timestamp TEXT
    );
    CREATE TABLE IF NOT EXISTS bot_settings (
        key   TEXT PRIMARY KEY,
        value TEXT
    );
    """)
    conn.commit(); conn.close()

init_db()

# ---------- settings ----------
def get_setting(key, default=""):
    conn = db(); c = conn.cursor()
    c.execute("SELECT value FROM bot_settings WHERE key=?", (key,))
    row = c.fetchone(); conn.close()
    return row[0] if row else default

def set_setting(key, value):
    conn = db(); c = conn.cursor()
    c.execute("REPLACE INTO bot_settings(key,value) VALUES(?,?)", (key, str(value)))
    conn.commit(); conn.close()

# ---------- users ----------
def get_user(uid):
    conn = db(); c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    row = c.fetchone(); conn.close(); return row

def save_user(uid, username="", first_name="", last_name="",
              country_code=None, assigned_number=None):
    existing = get_user(uid)
    if existing:
        country_code    = country_code    if country_code    is not None else existing[4]
        assigned_number = assigned_number if assigned_number is not None else existing[5]
        is_banned       = existing[6]
        join_date       = existing[7]
    else:
        is_banned = 0
        join_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = db(); c = conn.cursor()
    c.execute("""REPLACE INTO users
        (user_id, username, first_name, last_name, country_code,
         assigned_number, is_banned, join_date)
        VALUES (?,?,?,?,?,?,?,?)""",
        (uid, username, first_name, last_name,
         country_code, assigned_number, is_banned, join_date))
    conn.commit(); conn.close()

def get_all_users():
    conn = db(); c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE is_banned=0")
    out = [r[0] for r in c.fetchall()]; conn.close(); return out

def ban_user(uid):
    conn = db(); c = conn.cursor()
    c.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (uid,))
    conn.commit(); conn.close()

def unban_user(uid):
    conn = db(); c = conn.cursor()
    c.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (uid,))
    conn.commit(); conn.close()

def is_banned(uid):
    u = get_user(uid); return bool(u and u[6] == 1)

# ---------- combos ----------
def save_combo(code, numbers, custom_name=None):
    if not custom_name and code in COUNTRY_CODES:
        custom_name = COUNTRY_CODES[code][0]
    conn = db(); c = conn.cursor()
    c.execute("REPLACE INTO combos(country_code,custom_name,numbers) VALUES(?,?,?)",
              (code, custom_name, json.dumps(numbers)))
    conn.commit(); conn.close()

def get_combo(code):
    conn = db(); c = conn.cursor()
    c.execute("SELECT numbers FROM combos WHERE country_code=?", (code,))
    row = c.fetchone(); conn.close()
    return json.loads(row[0]) if row else []

def get_combo_name(code):
    conn = db(); c = conn.cursor()
    c.execute("SELECT custom_name FROM combos WHERE country_code=?", (code,))
    row = c.fetchone(); conn.close()
    if row and row[0]: return row[0]
    return COUNTRY_CODES.get(code, ("Unknown", "🌍"))[0]

def rename_combo(code, new_name):
    conn = db(); c = conn.cursor()
    c.execute("UPDATE combos SET custom_name=? WHERE country_code=?", (new_name, code))
    conn.commit(); conn.close()

def delete_combo(code):
    conn = db(); c = conn.cursor()
    c.execute("DELETE FROM combos WHERE country_code=?", (code,))
    conn.commit(); conn.close()

def get_all_combos():
    conn = db(); c = conn.cursor()
    c.execute("SELECT country_code FROM combos")
    out = [r[0] for r in c.fetchall()]; conn.close(); return out

def get_available_numbers(code):
    nums = get_combo(code)
    if not nums: return []
    conn = db(); c = conn.cursor()
    c.execute("SELECT assigned_number FROM users WHERE assigned_number IS NOT NULL AND assigned_number!=''")
    used = {r[0] for r in c.fetchall()}; conn.close()
    return [n for n in nums if n not in used]

def assign_number(uid, num):
    conn = db(); c = conn.cursor()
    c.execute("UPDATE users SET assigned_number=? WHERE user_id=?", (num, uid))
    conn.commit(); conn.close()

def release_number(num):
    if not num: return
    conn = db(); c = conn.cursor()
    c.execute("UPDATE users SET assigned_number=NULL WHERE assigned_number=?", (num,))
    conn.commit(); conn.close()

def get_user_by_number(num):
    conn = db(); c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE assigned_number=?", (num,))
    row = c.fetchone(); conn.close()
    return row[0] if row else None

# ---------- otp ----------
def log_otp(dt, num, cli, message, otp, country, service, sent_user=0, sent_group=0):
    conn = db(); c = conn.cursor()
    c.execute("""INSERT INTO otp_logs
        (dt,num,cli,message,otp,country,service,sent_to_user,sent_to_group,timestamp)
        VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (dt, num, cli, message, otp, country, service, sent_user, sent_group,
         datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit(); conn.close()

def get_otp_logs(limit=50):
    conn = db(); c = conn.cursor()
    c.execute("SELECT * FROM otp_logs ORDER BY id DESC LIMIT ?", (limit,))
    out = c.fetchall(); conn.close(); return out

def _hash_msg(dt, num, message):
    import hashlib
    return hashlib.md5(f"{dt}|{num}|{message}".encode()).hexdigest()

def already_sent(dt, num, message):
    h = _hash_msg(dt, num, message)
    conn = db(); c = conn.cursor()
    c.execute("SELECT 1 FROM sent_hashes WHERE h=?", (h,))
    exists = c.fetchone() is not None
    if not exists:
        c.execute("INSERT INTO sent_hashes(h,timestamp) VALUES(?,?)",
                  (h, datetime.now().isoformat()))
        conn.commit()
    conn.close()
    return exists

# ======================================================
# 🤖 إنشاء البوت
# ======================================================
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

def is_admin(uid):  return uid in ADMIN_IDS or uid == OWNER_ID
def is_owner(uid):  return uid == OWNER_ID

# ======================================================
# 🛠️ أدوات مساعدة
# ======================================================
def html_escape(t):
    if not t: return ""
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
                  .replace(">", "&gt;").replace('"', "&quot;"))

def mask_number(n):
    n = str(n or "").strip()
    if len(n) > 8: return n[:5] + "•••" + n[-3:]
    return n or "N/A"

def get_country_from_number(num):
    clean = re.sub(r"\D", "", str(num or ""))
    for code in sorted(COUNTRY_CODES.keys(), key=len, reverse=True):
        if clean.startswith(code):
            n, f = COUNTRY_CODES[code]; return n, f, code
    return "Unknown", "🌍", ""

def extract_otp(message):
    if not message: return "N/A"
    patterns = [
        r"(?:code|رمز|كود|verification|otp|pin|تحقق)[:\s\-]*[‎]?(\d{3,8})",
        r"\b(\d{3})[-\s](\d{3})\b",
        r"\b(\d{4,8})\b",
    ]
    for p in patterns:
        m = re.search(p, message, re.I)
        if m:
            g = m.groups()
            return "".join(g) if len(g) > 1 else g[0]
    return "N/A"

def detect_service(cli, msg):
    s = (cli or "").lower() + " " + (msg or "").lower()
    table = {
        "WHATSAPP": ["whatsapp", "واتس"],
        "TELEGRAM": ["telegram", "تيليج"],
        "FACEBOOK": ["facebook", "فيس", "fb"],
        "INSTAGRAM": ["instagram", "انست"],
        "GOOGLE":   ["google", "جوجل"],
        "TIKTOK":   ["tiktok", "تيك"],
        "TWITTER":  ["twitter", "x.com"],
        "DISCORD":  ["discord"],
        "APPLE":    ["apple"],
        "MICROSOFT":["microsoft"],
        "AMAZON":   ["amazon"],
        "PAYPAL":   ["paypal"],
        "NETFLIX":  ["netflix"],
        "UBER":     ["uber"],
    }
    for name, kws in table.items():
        if any(k in s for k in kws): return name
    return (cli or "GENERAL").upper()[:20]

# ======================================================
# 🔒 الاشتراك الإجباري
# ======================================================
def is_force_sub_enabled():
    return get_setting("force_sub", "off") == "on"

def check_user_joined(uid):
    try:
        for ch in FORCE_SUB_CHANNELS:
            username = ch.split("/")[-1]
            m = bot.get_chat_member(f"@{username}", uid)
            if m.status not in ("member", "administrator", "creator"):
                return False
        return True
    except Exception:
        return False

def send_force_sub(message):
    mk = types.InlineKeyboardMarkup()
    for i, ch in enumerate(FORCE_SUB_CHANNELS, 1):
        mk.add(types.InlineKeyboardButton(f"📢 Join Channel {i}", url=ch))
    mk.add(types.InlineKeyboardButton("✅ تحقّقت من الاشتراك", callback_data="check_sub"))
    bot.send_message(message.chat.id,
        "🔒 *للاستخدام يجب الاشتراك في القنوات أولاً ثم اضغط تحقق*",
        reply_markup=mk, parse_mode="Markdown")

# ======================================================
# 📨 تنسيق وإرسال OTP
# ======================================================
def format_otp_html(data):
    dt   = data.get("dt", "N/A")
    num  = data.get("num", "")
    cli  = data.get("cli", "")
    msg  = data.get("message", "")
    otp  = extract_otp(msg)
    srv  = detect_service(cli, msg)
    cname, flag, _ = get_country_from_number(num)
    masked = mask_number(num)

    html = (
f"""╭━━━━━━━━━━━━━━━━━━━╮
   {flag} <b>{cname} ~ {srv}</b>
╰━━━━━━━━━━━━━━━━━━━╯

⏰ <b>Time     :</b> <code>{html_escape(dt)}</code>
🌍 <b>Country  :</b> {flag} <b>{cname}</b>
⚙️ <b>Service  :</b> <code>{srv}</code>
📞 <b>Number   :</b> <code>{html_escape(masked)}</code>
🔑 <b>OTP Code :</b> <code>{html_escape(otp)}</code>

📩 <b>Full Message:</b>
<blockquote>{html_escape(msg)}</blockquote>

━━━━━━━━━━━━━━━━━━━━━
✨ <i>Powered by ZYRON SMS Bot</i>"""
    )
    return html, otp, cname, srv

def group_keyboard():
    mk = types.InlineKeyboardMarkup()
    mk.row(
        types.InlineKeyboardButton("👑 Owner",   url=OWNER_1_LINK),
        types.InlineKeyboardButton("📢 Channel", url=CHANNEL_1_URL),
    )
    mk.row(
        types.InlineKeyboardButton("👑 Owner 2",   url=OWNER_2_LINK),
        types.InlineKeyboardButton("📢 Channel 2", url=CHANNEL_2_URL),
    )
    return mk

def send_to_groups(text):
    ok = 0
    for cid in GROUP_CHAT_IDS:
        try:
            bot.send_message(cid, text, parse_mode="HTML",
                             reply_markup=group_keyboard(),
                             disable_web_page_preview=True)
            ok += 1
        except Exception as e:
            print(f"[!] إرسال جروب فشل {cid}: {e}")
    return ok > 0

def process_message(data):
    try:
        if already_sent(data.get("dt",""), data.get("num",""), data.get("message","")):
            return False

        text, otp, country, service = format_otp_html(data)
        group_ok = send_to_groups(text)

        # إرسال للمستخدم الذي يملك الرقم
        num = data.get("num", "")
        uid = get_user_by_number(num)
        user_sent = 0
        if uid:
            try:
                cname, flag, _ = get_country_from_number(num)
                user_msg = (
                    f"📥 <b>وصل رمز جديد!</b> {flag}\n\n"
                    f"⚙️ <b>Service :</b> <code>{service}</code>\n"
                    f"📞 <b>Number  :</b> <code>{html_escape(num)}</code>\n"
                    f"🌍 <b>Country :</b> {flag} {cname}\n"
                    f"🔑 <b>OTP     :</b> <code>{html_escape(otp)}</code>\n\n"
                    f"📩 <blockquote>{html_escape(data.get('message',''))}</blockquote>"
                )
                mk = types.InlineKeyboardMarkup()
                mk.row(
                    types.InlineKeyboardButton("👑 Owner",   url=OWNER_1_LINK),
                    types.InlineKeyboardButton("📢 Channel", url=CHANNEL_1_URL),
                )
                bot.send_message(uid, user_msg, parse_mode="HTML", reply_markup=mk)
                user_sent = 1
            except Exception as e:
                print(f"[!] فشل إرسال للمستخدم {uid}: {e}")

        log_otp(data.get("dt"), num, data.get("cli",""), data.get("message",""),
                otp, country, service, user_sent, 1 if group_ok else 0)
        print(f"[✓] {country} | {service} | {otp}")
        return True
    except Exception as e:
        print(f"[!] خطأ في المعالجة: {e}")
        traceback.print_exc()
        return False

# ======================================================
# 🔁 ثريد جلب الرسائل المستمر
# ======================================================
def fetcher_loop():
    print("🚀 بدأ ثريد جلب الرسائل من ZYRON...")
    while True:
        try:
            msgs = zyron.fetch_messages()
            for m in msgs:
                process_message(m)
        except Exception as e:
            print(f"[Loop] {e}")
        time.sleep(REFRESH_INTERVAL)

# ======================================================
# 🎮 /start ولوحة الدول
# ======================================================
def build_countries_keyboard(is_adm=False):
    mk = types.InlineKeyboardMarkup(row_width=2)
    combos = get_all_combos()
    row = []
    for code in combos:
        flag = COUNTRY_CODES.get(code, ("?", "🌍"))[1]
        name = get_combo_name(code)
        avail = len(get_available_numbers(code))
        row.append(types.InlineKeyboardButton(
            f"{flag} {name} ({avail})", callback_data=f"country_{code}"))
        if len(row) == 2:
            mk.row(*row); row = []
    if row: mk.row(*row)

    if is_adm:
        mk.add(types.InlineKeyboardButton("🛠️ لوحة الأدمن", callback_data="admin_panel"))
    mk.add(types.InlineKeyboardButton("👥 OTP GROUP", url=OTP_GROUP_LINK))
    return mk

@bot.message_handler(commands=["start"])
def cmd_start(message):
    uid = message.from_user.id

    if is_force_sub_enabled() and not is_admin(uid) and not check_user_joined(uid):
        send_force_sub(message); return

    if is_banned(uid):
        bot.reply_to(message, "🚫 أنت محظور من استخدام البوت."); return

    if not get_user(uid):
        for a in ADMIN_IDS:
            try:
                bot.send_message(a,
                    f"🆕 *مستخدم جديد*\n🆔 `{uid}`\n👤 @{message.from_user.username or '—'}",
                    parse_mode="Markdown")
            except: pass

    save_user(uid,
              username=message.from_user.username or "",
              first_name=message.from_user.first_name or "",
              last_name=message.from_user.last_name or "")

    combos = get_all_combos()
    adm = is_admin(uid)

    if not combos:
        if adm:
            mk = types.InlineKeyboardMarkup()
            mk.add(types.InlineKeyboardButton("🛠️ فتح لوحة الأدمن", callback_data="admin_panel"))
            mk.add(types.InlineKeyboardButton("📥 رفع كومبو الآن", callback_data="admin_add_combo"))
            bot.send_message(uid,
                "👋 *أهلاً أيها الأدمن!*\n\nلا توجد كومبوهات بعد.\n"
                "ارفع ملف TXT يحتوي أرقام دولة من زر *Add Combo* 👇",
                reply_markup=mk, parse_mode="Markdown")
        else:
            bot.send_message(uid,
                "⚠️ لا توجد دول متاحة حالياً.\nيرجى المحاولة لاحقاً أو التواصل مع الإدارة.")
        return

    bot.send_message(uid,
        "🌍 *اختر دولتك للحصول على رقم* 👇",
        reply_markup=build_countries_keyboard(adm),
        parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def cb_check_sub(call):
    if check_user_joined(call.from_user.id):
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        cmd_start(call.message if call.message.from_user.id == call.from_user.id else call.message)
        # تأكد من إرسال للمستخدم نفسه
        try:
            class _M: pass
            m = _M(); m.chat = call.message.chat
            m.from_user = call.from_user
            cmd_start(m)
        except: pass
    else:
        bot.answer_callback_query(call.id, "❌ لم تشترك بعد!", show_alert=True)

@bot.callback_query_handler(func=lambda c: c.data == "back_to_countries")
def cb_back_countries(call):
    adm = is_admin(call.from_user.id)
    try:
        bot.edit_message_text(
            "🌍 *اختر دولتك للحصول على رقم* 👇",
            call.message.chat.id, call.message.message_id,
            reply_markup=build_countries_keyboard(adm), parse_mode="Markdown")
    except: pass

@bot.callback_query_handler(func=lambda c: c.data.startswith("country_"))
def cb_country(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 محظور", show_alert=True); return
    code = call.data.split("_", 1)[1]
    avail = get_available_numbers(code)
    if not avail:
        bot.answer_callback_query(call.id, "❌ كل الأرقام محجوزة حالياً", show_alert=True); return

    u = get_user(call.from_user.id)
    if u and u[5]: release_number(u[5])

    num = random.choice(avail)
    assign_number(call.from_user.id, num)
    save_user(call.from_user.id, country_code=code, assigned_number=num)

    name, flag = COUNTRY_CODES.get(code, ("Unknown", "🌍"))
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🔄 تغيير الرقم", callback_data=f"change_{code}"))
    mk.add(types.InlineKeyboardButton("🌍 تغيير الدولة", callback_data="back_to_countries"))
    mk.add(types.InlineKeyboardButton("👥 OTP GROUP", url=OTP_GROUP_LINK))

    txt = (
f"""✅ <b>تم حجز الرقم لك</b>

📞 <b>Number  :</b> <code>{num}</code>
🌍 <b>Country :</b> {flag} {name}
⏳ <b>Status  :</b> <i>في انتظار وصول الكود...</i>

ℹ️ سيتم إرسال الكود تلقائياً هنا فور وصوله."""
    )
    try:
        bot.edit_message_text(txt, call.message.chat.id, call.message.message_id,
                              reply_markup=mk, parse_mode="HTML")
    except:
        bot.send_message(call.from_user.id, txt, reply_markup=mk, parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data.startswith("change_"))
def cb_change(call):
    call.data = "country_" + call.data.split("_", 1)[1]
    cb_country(call)

# ======================================================
# 🛠️ لوحة الأدمن
# ======================================================
def admin_menu():
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.row(
        types.InlineKeyboardButton("📥 رفع كومبو",  callback_data="admin_add_combo"),
        types.InlineKeyboardButton("🗑️ حذف كومبو", callback_data="admin_del_combo"),
    )
    mk.row(
        types.InlineKeyboardButton("✏️ تعديل اسم", callback_data="admin_rename"),
        types.InlineKeyboardButton("📊 إحصائيات",   callback_data="admin_stats"),
    )
    mk.row(
        types.InlineKeyboardButton("🚫 حظر",       callback_data="admin_ban"),
        types.InlineKeyboardButton("✅ فك حظر",    callback_data="admin_unban"),
    )
    mk.row(
        types.InlineKeyboardButton("📢 إذاعة للكل", callback_data="admin_bc_all"),
        types.InlineKeyboardButton("📨 إذاعة لواحد", callback_data="admin_bc_user"),
    )
    mk.row(
        types.InlineKeyboardButton("👤 معلومات مستخدم", callback_data="admin_user_info"),
        types.InlineKeyboardButton("🔒 الاشتراك الإجباري", callback_data="admin_toggle_fs"),
    )
    mk.row(
        types.InlineKeyboardButton("📄 تقرير كامل", callback_data="admin_report"),
        types.InlineKeyboardButton("🔙 رجوع",       callback_data="back_to_countries"),
    )
    return mk

@bot.callback_query_handler(func=lambda c: c.data == "admin_panel")
def cb_admin_panel(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ ممنوع", show_alert=True); return
    fs = "🟢 ON" if is_force_sub_enabled() else "🔴 OFF"
    txt = (
        "🛠️ <b>لوحة تحكّم الأدمن</b>\n\n"
        f"👑 الأدمنز: <code>{len(ADMIN_IDS)}</code>\n"
        f"🔒 الاشتراك الإجباري: <b>{fs}</b>\n\n"
        "اختر إجراء من الأسفل 👇"
    )
    try:
        bot.edit_message_text(txt, call.message.chat.id, call.message.message_id,
                              reply_markup=admin_menu(), parse_mode="HTML")
    except:
        bot.send_message(call.from_user.id, txt, reply_markup=admin_menu(), parse_mode="HTML")

# --- رفع كومبو ---
@bot.callback_query_handler(func=lambda c: c.data == "admin_add_combo")
def cb_add_combo(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "waiting_combo"
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
    bot.edit_message_text(
        "📤 *أرسل الآن ملف TXT يحتوي الأرقام*\n"
        "_سيتم اكتشاف كود الدولة تلقائياً._",
        call.message.chat.id, call.message.message_id,
        reply_markup=mk, parse_mode="Markdown")

@bot.message_handler(content_types=["document"])
def handle_doc(message):
    if not is_admin(message.from_user.id): return
    if user_states.get(message.from_user.id) != "waiting_combo": return

    try:
        info = bot.get_file(message.document.file_id)
        data = bot.download_file(info.file_path).decode("utf-8", errors="ignore")

        nums = []
        for line in data.splitlines():
            clean = re.sub(r"[^\d+]", "", line)
            for m in re.findall(r"\d{8,15}", clean):
                if m.startswith("0"): m = m[1:]
                if len(m) >= 8: nums.append(m)

        if not nums:
            bot.reply_to(message, "❌ لم أعثر على أرقام صالحة!"); return

        # اكتشاف الكود
        counts = {}
        for n in nums[:200]:
            for code in sorted(COUNTRY_CODES.keys(), key=len, reverse=True):
                if n.startswith(code):
                    counts[code] = counts.get(code, 0) + 1; break
        if not counts:
            bot.reply_to(message, "❌ لم أتمكن من تحديد كود الدولة."); return

        best = max(counts.items(), key=lambda x: x[1])[0]
        name, flag = COUNTRY_CODES[best]
        save_combo(best, nums)

        user_states.pop(message.from_user.id, None)
        bot.reply_to(message,
            f"✅ *تم حفظ الكومبو بنجاح!*\n\n"
            f"{flag} *الدولة:* {name}\n"
            f"📞 *الكود:* +{best}\n"
            f"🔢 *الأرقام:* {len(nums)}\n"
            f"🕒 {datetime.now():%Y-%m-%d %H:%M:%S}",
            parse_mode="Markdown")
    except Exception as e:
        traceback.print_exc()
        bot.reply_to(message, f"❌ خطأ: {e}")
        user_states.pop(message.from_user.id, None)

# --- حذف كومبو ---
@bot.callback_query_handler(func=lambda c: c.data == "admin_del_combo")
def cb_del_combo(call):
    if not is_admin(call.from_user.id): return
    combos = get_all_combos()
    if not combos:
        bot.answer_callback_query(call.id, "لا توجد كومبوهات!", show_alert=True); return
    mk = types.InlineKeyboardMarkup()
    for code in combos:
        n, f = COUNTRY_CODES.get(code, ("?", "🌍"))
        mk.add(types.InlineKeyboardButton(f"{f} {get_combo_name(code)}",
                                          callback_data=f"delc_{code}"))
    mk.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
    bot.edit_message_text("اختر الكومبو المراد حذفه:", call.message.chat.id,
                          call.message.message_id, reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("delc_"))
def cb_del_combo_confirm(call):
    if not is_admin(call.from_user.id): return
    code = call.data.split("_", 1)[1]
    delete_combo(code)
    bot.answer_callback_query(call.id, "✅ حُذف")
    cb_admin_panel(call)

# --- إعادة تسمية ---
@bot.callback_query_handler(func=lambda c: c.data == "admin_rename")
def cb_rename_list(call):
    if not is_admin(call.from_user.id): return
    combos = get_all_combos()
    mk = types.InlineKeyboardMarkup()
    for code in combos:
        mk.add(types.InlineKeyboardButton(get_combo_name(code),
                                          callback_data=f"ren_{code}"))
    mk.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
    bot.edit_message_text("اختر الكومبو لإعادة التسمية:", call.message.chat.id,
                          call.message.message_id, reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("ren_"))
def cb_rename_ask(call):
    if not is_admin(call.from_user.id): return
    code = call.data.split("_", 1)[1]
    user_states[call.from_user.id] = f"rename_{code}"
    bot.send_message(call.from_user.id, "✏️ أرسل الاسم الجديد:")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, "").startswith("rename_"))
def msg_rename(message):
    code = user_states[message.from_user.id].split("_", 1)[1]
    rename_combo(code, message.text.strip()[:50])
    user_states.pop(message.from_user.id, None)
    bot.reply_to(message, "✅ تم تحديث الاسم.")

# --- إحصائيات ---
@bot.callback_query_handler(func=lambda c: c.data == "admin_stats")
def cb_stats(call):
    if not is_admin(call.from_user.id): return
    combos = get_all_combos()
    total_nums = sum(len(get_combo(c)) for c in combos)
    txt = (
        "📊 <b>إحصائيات البوت</b>\n\n"
        f"👥 المستخدمون النشطون: <code>{len(get_all_users())}</code>\n"
        f"🌐 الدول: <code>{len(combos)}</code>\n"
        f"📞 إجمالي الأرقام: <code>{total_nums}</code>\n"
        f"🔑 إجمالي الأكواد: <code>{len(get_otp_logs(99999))}</code>\n"
        f"📡 الاتصال بـ ZYRON: <b>{'🟢' if zyron.is_logged_in else '🔴'}</b>\n\n"
        "<b>تفاصيل الدول:</b>\n"
    )
    for code in combos:
        n, f = COUNTRY_CODES.get(code, ("?", "🌍"))
        avail = len(get_available_numbers(code))
        total = len(get_combo(code))
        txt += f"{f} {get_combo_name(code)} — <code>{avail}/{total}</code>\n"
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id,
                          reply_markup=mk, parse_mode="HTML")

# --- حظر / فك حظر ---
@bot.callback_query_handler(func=lambda c: c.data == "admin_ban")
def cb_ban(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "ban_uid"
    bot.send_message(call.from_user.id, "🚫 أرسل ID المستخدم لحظره:")

@bot.callback_query_handler(func=lambda c: c.data == "admin_unban")
def cb_unban(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "unban_uid"
    bot.send_message(call.from_user.id, "✅ أرسل ID المستخدم لفك حظره:")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) in ("ban_uid","unban_uid"))
def msg_ban_unban(message):
    state = user_states.pop(message.from_user.id, "")
    try:
        uid = int(message.text)
        if state == "ban_uid":
            ban_user(uid);   bot.reply_to(message, f"🚫 تم حظر {uid}")
        else:
            unban_user(uid); bot.reply_to(message, f"✅ تم فك حظر {uid}")
    except:
        bot.reply_to(message, "❌ ID غير صحيح")

# --- إذاعة ---
@bot.callback_query_handler(func=lambda c: c.data == "admin_bc_all")
def cb_bc_all(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "bc_all"
    bot.send_message(call.from_user.id, "📢 أرسل الرسالة التي تريد إذاعتها للجميع:")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "bc_all",
                     content_types=["text", "photo"])
def msg_bc_all(message):
    user_states.pop(message.from_user.id, None)
    users = get_all_users()
    ok = 0
    for uid in users:
        try:
            if message.content_type == "photo":
                bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption or "")
            else:
                bot.send_message(uid, message.text)
            ok += 1
        except: pass
    bot.reply_to(message, f"✅ تم الإرسال إلى {ok}/{len(users)}")

@bot.callback_query_handler(func=lambda c: c.data == "admin_bc_user")
def cb_bc_user(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "bcu_uid"
    bot.send_message(call.from_user.id, "📨 أرسل ID المستخدم:")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "bcu_uid")
def msg_bcu_uid(message):
    try:
        uid = int(message.text)
        user_states[message.from_user.id] = f"bcu_msg_{uid}"
        bot.reply_to(message, "أرسل الرسالة الآن:")
    except:
        bot.reply_to(message, "❌ ID غير صحيح")
        user_states.pop(message.from_user.id, None)

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, "").startswith("bcu_msg_"))
def msg_bcu_send(message):
    uid = int(user_states.pop(message.from_user.id).split("_")[2])
    try:
        bot.send_message(uid, message.text)
        bot.reply_to(message, f"✅ أُرسلت إلى {uid}")
    except Exception as e:
        bot.reply_to(message, f"❌ فشل: {e}")

# --- معلومات مستخدم ---
@bot.callback_query_handler(func=lambda c: c.data == "admin_user_info")
def cb_uinfo(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "uinfo"
    bot.send_message(call.from_user.id, "👤 أرسل ID المستخدم:")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "uinfo")
def msg_uinfo(message):
    user_states.pop(message.from_user.id, None)
    try:
        uid = int(message.text)
        u = get_user(uid)
        if not u:
            bot.reply_to(message, "❌ غير موجود"); return
        status = "🚫 محظور" if u[6] else "🟢 نشط"
        txt = (
            f"👤 <b>معلومات المستخدم</b>\n\n"
            f"🆔 <code>{u[0]}</code>\n"
            f"👤 @{u[1] or '—'}\n"
            f"الاسم: {u[2] or ''} {u[3] or ''}\n"
            f"🌍 كود الدولة: <code>{u[4] or '—'}</code>\n"
            f"📞 الرقم المحجوز: <code>{u[5] or '—'}</code>\n"
            f"الحالة: {status}\n"
            f"📅 التسجيل: {u[7] or '—'}"
        )
        bot.reply_to(message, txt, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ {e}")

# --- toggle force sub ---
@bot.callback_query_handler(func=lambda c: c.data == "admin_toggle_fs")
def cb_toggle_fs(call):
    if not is_admin(call.from_user.id): return
    if is_force_sub_enabled():
        set_setting("force_sub", "off")
        bot.answer_callback_query(call.id, "🔴 الاشتراك الإجباري معطّل")
    else:
        set_setting("force_sub", "on")
        bot.answer_callback_query(call.id, "🟢 الاشتراك الإجباري مفعّل")
    cb_admin_panel(call)

# --- تقرير ---
@bot.callback_query_handler(func=lambda c: c.data == "admin_report")
def cb_report(call):
    if not is_admin(call.from_user.id): return
    try:
        path = "/tmp/zyron_report.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"ZYRON BOT REPORT — {datetime.now()}\n" + "="*50 + "\n\n")
            f.write("👥 USERS:\n")
            conn = db(); c = conn.cursor()
            for u in c.execute("SELECT * FROM users").fetchall():
                f.write(f"  {u[0]} | @{u[1] or '-'} | banned={u[6]} | num={u[5] or '-'}\n")
            f.write("\n🔑 LAST 100 OTPs:\n")
            for o in c.execute("SELECT * FROM otp_logs ORDER BY id DESC LIMIT 100").fetchall():
                f.write(f"  {o[10]} | {o[2]} | {o[6]} | {o[7]} | OTP={o[5]}\n")
            conn.close()
        with open(path, "rb") as f:
            bot.send_document(call.from_user.id, f)
        os.remove(path)
        bot.answer_callback_query(call.id, "📄 تم")
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ {e}", show_alert=True)

# ======================================================
# ▶️ تشغيل البوت
# ======================================================
def main():
    print("="*50)
    print("  ZYRON SMS Bot — Starting...")
    print("="*50)

    # محاولة تسجيل دخول للموقع
    zyron.login()

    # ثريد جلب الرسائل
    t = threading.Thread(target=fetcher_loop, daemon=True)
    t.start()

    print("🤖 البوت يعمل... اضغط Ctrl+C للإيقاف")
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=30, skip_pending=True)
        except Exception as e:
            print(f"[polling crashed] {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
