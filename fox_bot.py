# -*- coding: utf-8 -*-
"""
FOX Bot Number — Telegram bot + Embedded Telegram WebApp (Mini App)
====================================================================
- Single Python file
- Built-in Flask micro web server serves a colorful Mini App UI
- Telegram /start opens the WebApp via KeyboardButton(web_app=...)
- All numbers / OTPs / users live in sqlite3
- Panel scraper (Zyron / IVASMS style) fetches SMS and pushes OTPs

Install:
    pip install pyTelegramBotAPI requests beautifulsoup4 flask

Run:
    python fox_bot.py

⚠️ Telegram WebApp requires HTTPS. For local testing use ngrok:
    ngrok http 8080
    -> copy the https URL into WEBAPP_URL below
"""

import os, re, time, json, html, sqlite3, threading, logging, hmac, hashlib
from urllib.parse import parse_qsl
from datetime import datetime
from typing import Optional, List, Dict, Tuple

import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
from flask import Flask, request, jsonify, Response

# ============================================================
# CONFIG
# ============================================================
BOT_TOKEN      = "8794957674:AAHzev14d5JM7F3IpOQaCn-J_hRNSuGVrn8"
ADMIN_IDS      = [8761832730]
SITE_BASE      = "http://151.80.19.204/ints"
SITE_USERNAME  = "Hama11"
SITE_PASSWORD  = "Hama11"
GROUP_LINK     = "https://t.me/+IaUh8c8vXnIzYTM0"
REWARD_PER_OTP = 0.0030
NUMBERS_PER_REQUEST = 4
FETCH_INTERVAL = 8
DB_PATH        = "fox_bot.db"

# الويب أب — يجب أن يكون HTTPS عند النشر للتيليجرام
WEB_HOST   = "0.0.0.0"
WEB_PORT   = 8080
WEBAPP_URL = "https://bot-new-8zzw.onrender.com"   # ← غيّره (https إلزامي)

WELCOME_STICKER_ID = "CAACAgIAAxkBAAEBQYZl4n5hWfQ"

PLATFORMS = {
    "facebook":  {"name": "Facebook",  "emoji": "📘", "color": "#1877F2", "keywords": ["facebook", "fb", "meta"]},
    "whatsapp":  {"name": "WhatsApp",  "emoji": "🟢", "color": "#25D366", "keywords": ["whatsapp", "wa"]},
    "imo":       {"name": "IMO",       "emoji": "🌟", "color": "#5B5BFF", "keywords": ["imo"]},
    "tiktok":    {"name": "TikTok",    "emoji": "🎵", "color": "#111111", "keywords": ["tiktok", "tik tok"]},
    "instagram": {"name": "Instagram", "emoji": "📸", "color": "#E1306C", "keywords": ["instagram", "insta", "ig"]},
    "telegram":  {"name": "Telegram",  "emoji": "✈️", "color": "#229ED9", "keywords": ["telegram", "tg"]},
    "google":    {"name": "Google",    "emoji": "🔎", "color": "#EA4335", "keywords": ["google", "gmail"]},
    "twitter":   {"name": "Twitter/X", "emoji": "🐦", "color": "#1DA1F2", "keywords": ["twitter", "x.com"]},
    "other":     {"name": "Other",     "emoji": "🗂️", "color": "#6B7280", "keywords": []},
}

# (code, en, ar, flag)  — من الأطول للأقصر لمطابقة 1xxx قبل 1
COUNTRIES_RAW = [
    ("93","Afghanistan","أفغانستان","🇦🇫"),("355","Albania","ألبانيا","🇦🇱"),
    ("213","Algeria","الجزائر","🇩🇿"),("376","Andorra","أندورا","🇦🇩"),
    ("244","Angola","أنغولا","🇦🇴"),("1264","Anguilla","أنغويلا","🇦🇮"),
    ("1268","Antigua","أنتيغوا","🇦🇬"),("54","Argentina","الأرجنتين","🇦🇷"),
    ("374","Armenia","أرمينيا","🇦🇲"),("297","Aruba","أروبا","🇦🇼"),
    ("61","Australia","أستراليا","🇦🇺"),("43","Austria","النمسا","🇦🇹"),
    ("994","Azerbaijan","أذربيجان","🇦🇿"),("1242","Bahamas","الباهاما","🇧🇸"),
    ("973","Bahrain","البحرين","🇧🇭"),("880","Bangladesh","بنغلاديش","🇧🇩"),
    ("1246","Barbados","بربادوس","🇧🇧"),("375","Belarus","بيلاروسيا","🇧🇾"),
    ("32","Belgium","بلجيكا","🇧🇪"),("501","Belize","بليز","🇧🇿"),
    ("229","Benin","بنين","🇧🇯"),("1441","Bermuda","برمودا","🇧🇲"),
    ("975","Bhutan","بوتان","🇧🇹"),("591","Bolivia","بوليفيا","🇧🇴"),
    ("387","Bosnia","البوسنة","🇧🇦"),("267","Botswana","بوتسوانا","🇧🇼"),
    ("55","Brazil","البرازيل","🇧🇷"),("673","Brunei","بروناي","🇧🇳"),
    ("359","Bulgaria","بلغاريا","🇧🇬"),("226","Burkina Faso","بوركينا فاسو","🇧🇫"),
    ("257","Burundi","بوروندي","🇧🇮"),("855","Cambodia","كمبوديا","🇰🇭"),
    ("237","Cameroon","الكاميرون","🇨🇲"),("1","Canada/USA","كندا/أمريكا","🇺🇸"),
    ("238","Cape Verde","الرأس الأخضر","🇨🇻"),("1345","Cayman","كايمان","🇰🇾"),
    ("236","Central Africa","إفريقيا الوسطى","🇨🇫"),("235","Chad","تشاد","🇹🇩"),
    ("56","Chile","تشيلي","🇨🇱"),("86","China","الصين","🇨🇳"),
    ("57","Colombia","كولومبيا","🇨🇴"),("269","Comoros","جزر القمر","🇰🇲"),
    ("242","Congo","الكونغو","🇨🇬"),("243","DR Congo","الكونغو الديمقراطية","🇨🇩"),
    ("506","Costa Rica","كوستاريكا","🇨🇷"),("385","Croatia","كرواتيا","🇭🇷"),
    ("53","Cuba","كوبا","🇨🇺"),("357","Cyprus","قبرص","🇨🇾"),
    ("420","Czech","التشيك","🇨🇿"),("45","Denmark","الدنمارك","🇩🇰"),
    ("253","Djibouti","جيبوتي","🇩🇯"),("1767","Dominica","دومينيكا","🇩🇲"),
    ("1809","Dominican Rep.","الدومينيكان","🇩🇴"),("593","Ecuador","الإكوادور","🇪🇨"),
    ("20","Egypt","مصر","🇪🇬"),("503","El Salvador","السلفادور","🇸🇻"),
    ("240","Eq. Guinea","غينيا الاستوائية","🇬🇶"),("291","Eritrea","إريتريا","🇪🇷"),
    ("372","Estonia","إستونيا","🇪🇪"),("251","Ethiopia","إثيوبيا","🇪🇹"),
    ("298","Faroe","فارو","🇫🇴"),("679","Fiji","فيجي","🇫🇯"),
    ("358","Finland","فنلندا","🇫🇮"),("33","France","فرنسا","🇫🇷"),
    ("594","Fr. Guiana","غويانا الفرنسية","🇬🇫"),("689","Fr. Polynesia","بولينيزيا","🇵🇫"),
    ("241","Gabon","الغابون","🇬🇦"),("220","Gambia","غامبيا","🇬🇲"),
    ("995","Georgia","جورجيا","🇬🇪"),("49","Germany","ألمانيا","🇩🇪"),
    ("233","Ghana","غانا","🇬🇭"),("350","Gibraltar","جبل طارق","🇬🇮"),
    ("30","Greece","اليونان","🇬🇷"),("299","Greenland","جرينلاند","🇬🇱"),
    ("1473","Grenada","غرينادا","🇬🇩"),("590","Guadeloupe","غوادلوب","🇬🇵"),
    ("1671","Guam","غوام","🇬🇺"),("502","Guatemala","غواتيمالا","🇬🇹"),
    ("224","Guinea","غينيا","🇬🇳"),("245","Guinea-Bissau","غينيا بيساو","🇬🇼"),
    ("592","Guyana","غيانا","🇬🇾"),("509","Haiti","هايتي","🇭🇹"),
    ("504","Honduras","هندوراس","🇭🇳"),("852","Hong Kong","هونغ كونغ","🇭🇰"),
    ("36","Hungary","المجر","🇭🇺"),("354","Iceland","آيسلندا","🇮🇸"),
    ("91","India","الهند","🇮🇳"),("62","Indonesia","إندونيسيا","🇮🇩"),
    ("98","Iran","إيران","🇮🇷"),("964","Iraq","العراق","🇮🇶"),
    ("353","Ireland","أيرلندا","🇮🇪"),("972","Palestine","فلسطين","🇵🇸"),
    ("39","Italy","إيطاليا","🇮🇹"),("225","Ivory Coast","ساحل العاج","🇨🇮"),
    ("1876","Jamaica","جامايكا","🇯🇲"),("81","Japan","اليابان","🇯🇵"),
    ("962","Jordan","الأردن","🇯🇴"),("7","Kazakhstan/Russia","كازاخستان/روسيا","🇰🇿"),
    ("254","Kenya","كينيا","🇰🇪"),("686","Kiribati","كيريباتي","🇰🇮"),
    ("383","Kosovo","كوسوفو","🇽🇰"),("965","Kuwait","الكويت","🇰🇼"),
    ("996","Kyrgyzstan","قرغيزستان","🇰🇬"),("856","Laos","لاوس","🇱🇦"),
    ("371","Latvia","لاتفيا","🇱🇻"),("961","Lebanon","لبنان","🇱🇧"),
    ("266","Lesotho","ليسوتو","🇱🇸"),("231","Liberia","ليبيريا","🇱🇷"),
    ("218","Libya","ليبيا","🇱🇾"),("423","Liechtenstein","ليختنشتاين","🇱🇮"),
    ("370","Lithuania","ليتوانيا","🇱🇹"),("352","Luxembourg","لوكسمبورغ","🇱🇺"),
    ("853","Macau","ماكاو","🇲🇴"),("389","N. Macedonia","مقدونيا","🇲🇰"),
    ("261","Madagascar","مدغشقر","🇲🇬"),("265","Malawi","مالاوي","🇲🇼"),
    ("60","Malaysia","ماليزيا","🇲🇾"),("960","Maldives","المالديف","🇲🇻"),
    ("223","Mali","مالي","🇲🇱"),("356","Malta","مالطا","🇲🇹"),
    ("692","Marshall","مارشال","🇲🇭"),("596","Martinique","مارتينيك","🇲🇶"),
    ("222","Mauritania","موريتانيا","🇲🇷"),("230","Mauritius","موريشيوس","🇲🇺"),
    ("52","Mexico","المكسيك","🇲🇽"),("691","Micronesia","ميكرونيزيا","🇫🇲"),
    ("373","Moldova","مولدوفا","🇲🇩"),("377","Monaco","موناكو","🇲🇨"),
    ("976","Mongolia","منغوليا","🇲🇳"),("382","Montenegro","الجبل الأسود","🇲🇪"),
    ("1664","Montserrat","مونتسيرات","🇲🇸"),("212","Morocco","المغرب","🇲🇦"),
    ("258","Mozambique","موزمبيق","🇲🇿"),("95","Myanmar","ميانمار","🇲🇲"),
    ("264","Namibia","ناميبيا","🇳🇦"),("674","Nauru","ناورو","🇳🇷"),
    ("977","Nepal","نيبال","🇳🇵"),("31","Netherlands","هولندا","🇳🇱"),
    ("687","New Caledonia","كاليدونيا","🇳🇨"),("64","New Zealand","نيوزيلندا","🇳🇿"),
    ("505","Nicaragua","نيكاراغوا","🇳🇮"),("227","Niger","النيجر","🇳🇪"),
    ("234","Nigeria","نيجيريا","🇳🇬"),("850","North Korea","كوريا الشمالية","🇰🇵"),
    ("47","Norway","النرويج","🇳🇴"),("968","Oman","عُمان","🇴🇲"),
    ("92","Pakistan","باكستان","🇵🇰"),("680","Palau","بالاو","🇵🇼"),
    ("507","Panama","بنما","🇵🇦"),("675","Papua","بابوا","🇵🇬"),
    ("595","Paraguay","باراغواي","🇵🇾"),("51","Peru","البيرو","🇵🇪"),
    ("63","Philippines","الفلبين","🇵🇭"),("48","Poland","بولندا","🇵🇱"),
    ("351","Portugal","البرتغال","🇵🇹"),("1787","Puerto Rico","بورتوريكو","🇵🇷"),
    ("974","Qatar","قطر","🇶🇦"),("262","Réunion","ريونيون","🇷🇪"),
    ("40","Romania","رومانيا","🇷🇴"),("250","Rwanda","رواندا","🇷🇼"),
    ("290","St Helena","سانت هيلينا","🇸🇭"),("1869","St Kitts","سانت كيتس","🇰🇳"),
    ("1758","St Lucia","سانت لوسيا","🇱🇨"),("1784","St Vincent","سانت فنسنت","🇻🇨"),
    ("685","Samoa","ساموا","🇼🇸"),("378","San Marino","سان مارينو","🇸🇲"),
    ("239","Sao Tome","ساو تومي","🇸🇹"),("966","Saudi Arabia","السعودية","🇸🇦"),
    ("221","Senegal","السنغال","🇸🇳"),("381","Serbia","صربيا","🇷🇸"),
    ("248","Seychelles","سيشل","🇸🇨"),("232","Sierra Leone","سيراليون","🇸🇱"),
    ("65","Singapore","سنغافورة","🇸🇬"),("421","Slovakia","سلوفاكيا","🇸🇰"),
    ("386","Slovenia","سلوفينيا","🇸🇮"),("677","Solomon","سليمان","🇸🇧"),
    ("252","Somalia","الصومال","🇸🇴"),("27","South Africa","جنوب إفريقيا","🇿🇦"),
    ("82","South Korea","كوريا الجنوبية","🇰🇷"),("211","South Sudan","جنوب السودان","🇸🇸"),
    ("34","Spain","إسبانيا","🇪🇸"),("94","Sri Lanka","سريلانكا","🇱🇰"),
    ("249","Sudan","السودان","🇸🇩"),("597","Suriname","سورينام","🇸🇷"),
    ("268","Eswatini","إسواتيني","🇸🇿"),("46","Sweden","السويد","🇸🇪"),
    ("41","Switzerland","سويسرا","🇨🇭"),("963","Syria","سوريا","🇸🇾"),
    ("886","Taiwan","تايوان","🇹🇼"),("992","Tajikistan","طاجيكستان","🇹🇯"),
    ("255","Tanzania","تنزانيا","🇹🇿"),("66","Thailand","تايلاند","🇹🇭"),
    ("670","Timor","تيمور","🇹🇱"),("228","Togo","توغو","🇹🇬"),
    ("676","Tonga","تونغا","🇹🇴"),("1868","Trinidad","ترينيداد","🇹🇹"),
    ("216","Tunisia","تونس","🇹🇳"),("90","Turkey","تركيا","🇹🇷"),
    ("993","Turkmenistan","تركمانستان","🇹🇲"),("688","Tuvalu","توفالو","🇹🇻"),
    ("256","Uganda","أوغندا","🇺🇬"),("380","Ukraine","أوكرانيا","🇺🇦"),
    ("971","UAE","الإمارات","🇦🇪"),("44","UK","المملكة المتحدة","🇬🇧"),
    ("598","Uruguay","الأوروغواي","🇺🇾"),("998","Uzbekistan","أوزبكستان","🇺🇿"),
    ("678","Vanuatu","فانواتو","🇻🇺"),("58","Venezuela","فنزويلا","🇻🇪"),
    ("84","Vietnam","فيتنام","🇻🇳"),("967","Yemen","اليمن","🇾🇪"),
    ("260","Zambia","زامبيا","🇿🇲"),("263","Zimbabwe","زيمبابوي","🇿🇼"),
]
COUNTRIES_SORTED = sorted(COUNTRIES_RAW, key=lambda x: -len(x[0]))
COUNTRY_MAP = {code: (en, ar, fl) for code, en, ar, fl in COUNTRIES_RAW}


def detect_country(number: str) -> Tuple[str, str, str, str]:
    num = re.sub(r"\D", "", number or "")
    for code, en, ar, flag in COUNTRIES_SORTED:
        if num.startswith(code):
            return code, en, ar, flag
    return "?", "Unknown", "غير معروف", "🏳️"


# ============================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("fox-bot")


# ============================================================
# DB
# ============================================================
def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    c = db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
        balance REAL DEFAULT 0, total_received INTEGER DEFAULT 0,
        banned INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS numbers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT, country_code TEXT, number TEXT UNIQUE,
        status TEXT DEFAULT 'free', assigned_to INTEGER, assigned_at TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS otps(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT, country_code TEXT, number TEXT, code TEXT,
        full_sms TEXT, hash_key TEXT UNIQUE, delivered_to INTEGER,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_num_pool ON numbers(platform, country_code, status);
    """)
    c.commit(); c.close()


# ============================================================
# Panel client (unchanged logic)
# ============================================================
class PanelClient:
    def __init__(self, base, user, pwd):
        self.base = base.rstrip("/"); self.user = user; self.pwd = pwd
        self.s = requests.Session()
        self.s.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        })
        self.logged_in = False; self.lock = threading.Lock()

    def _solve(self, text):
        m = re.search(r"(\d+)\s*([\+\-\*])\s*(\d+)", text)
        if not m: return None
        a, op, b = int(m.group(1)), m.group(2), int(m.group(3))
        return str({"+":a+b,"-":a-b,"*":a*b}[op])

    def login(self):
        try:
            r = self.s.get(f"{self.base}/login", timeout=20)
            soup = BeautifulSoup(r.text, "html.parser")
            tok = soup.find("input", {"name":"_token"})
            token = tok["value"] if tok else ""
            data = {"_token":token,"email":self.user,"password":self.pwd,
                    "capt":self._solve(r.text) or ""}
            r2 = self.s.post(f"{self.base}/signin", data=data,
                             headers={"Referer":f"{self.base}/login"},
                             timeout=20, allow_redirects=True)
            self.logged_in = ("logout" in r2.text.lower() or "dashboard" in r2.url.lower()
                              or "client" in r2.url.lower())
            log.info(f"Login -> {self.logged_in}")
            return self.logged_in
        except Exception as e:
            log.error(f"login: {e}"); return False

    def fetch_sms(self):
        with self.lock:
            if not self.logged_in and not self.login(): return []
            today = datetime.utcnow().strftime("%Y-%m-%d")
            params = {"fdate1":f"{today} 00:00:00","fdate2":f"{today} 23:59:59",
                      "frange":"","fclient":"","fnum":"","fcli":"","fgdate":"",
                      "fgmonth":"","fgrange":"","fgclient":"","fgnumber":"","fgcli":"",
                      "fg":"0","iDisplayStart":0,"iDisplayLength":50}
            try:
                r = self.s.get(f"{self.base}/client/res/data_smscdr.php", params=params,
                               timeout=20, headers={
                                   "Referer":f"{self.base}/client/SMSCDRStats",
                                   "X-Requested-With":"XMLHttpRequest"})
                if r.status_code == 401 or "login" in r.url:
                    self.logged_in = False; self.login(); return []
                data = r.json(); out = []
                for row in data.get("aaData", []):
                    cells = [BeautifulSoup(str(c),"html.parser").get_text(" ",strip=True) for c in row]
                    joined = " | ".join(cells)
                    m = re.search(r"(\+?\d{8,15})", joined)
                    if not m: continue
                    out.append({"number":m.group(1).lstrip("+"),
                                "sms":cells[-1] if cells else "", "raw":joined})
                return out
            except Exception as e:
                log.error(f"fetch_sms: {e}"); self.logged_in=False; return []


panel = PanelClient(SITE_BASE, SITE_USERNAME, SITE_PASSWORD)
OTP_REGEX = re.compile(r"(\b\d{3}[- ]?\d{3,4}\b|\b\d{4,8}\b)")

def extract_code(s): m = OTP_REGEX.search(s or ""); return m.group(1) if m else None
def detect_platform(s):
    s = (s or "").lower()
    for pid,p in PLATFORMS.items():
        if pid=="other": continue
        for k in p["keywords"]:
            if k in s: return pid
    return "other"
def hash_key(n,c): return f"{n}:{c}"


# ============================================================
# Telegram WebApp initData verification
# ============================================================
def verify_init_data(init_data: str) -> Optional[dict]:
    """Validates Telegram WebApp initData. Returns parsed user dict or None."""
    try:
        parsed = dict(parse_qsl(init_data, keep_blank_values=True))
        recv_hash = parsed.pop("hash", None)
        if not recv_hash: return None
        check_string = "\n".join(f"{k}={parsed[k]}" for k in sorted(parsed))
        secret = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        calc = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
        if calc != recv_hash: return None
        user = json.loads(parsed.get("user", "{}"))
        return user
    except Exception:
        return None


def get_user_from_request() -> Optional[dict]:
    init_data = request.headers.get("X-Init-Data") or request.args.get("initData", "")
    u = verify_init_data(init_data) if init_data else None
    # وضع التطوير: لو ما في initData اعتبره ضيف برقم 0 (للاختبار محلياً)
    if not u and request.args.get("dev") == "1":
        return {"id": 0, "first_name": "Dev"}
    return u


# ============================================================
# Flask Mini App
# ============================================================
app = Flask(__name__)

INDEX_HTML = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>FOX Bot Number</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
:root{
  --bg:#0b1220; --panel:#111a2e; --text:#eaf2ff; --muted:#9fb0c9;
  --blue1:#2563eb; --blue2:#06b6d4; --green1:#16a34a; --green2:#22c55e;
  --red1:#dc2626; --red2:#ef4444; --gold:#f59e0b; --shadow:0 8px 20px rgba(0,0,0,.35);
}
*{box-sizing:border-box} html,body{margin:0;padding:0;background:var(--bg);color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",Roboto,system-ui,sans-serif}
.app{max-width:560px;margin:0 auto;padding:16px;padding-bottom:40px}
.header{display:flex;align-items:center;gap:12px;margin-bottom:14px}
.logo{width:54px;height:54px;border-radius:14px;background:conic-gradient(from 0deg,#22c55e,#06b6d4,#2563eb,#a855f7,#22c55e);
  animation:spin 6s linear infinite;box-shadow:var(--shadow);display:flex;align-items:center;justify-content:center;font-size:26px}
@keyframes spin{to{transform:rotate(360deg)}}
.title{font-weight:800;font-size:20px}.sub{color:var(--muted);font-size:13px}
.card{background:var(--panel);border:1px solid #1f2a44;border-radius:18px;padding:14px;margin:12px 0;box-shadow:var(--shadow)}
.btn{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:16px;border:0;border-radius:14px;
  font-size:16px;font-weight:700;color:#fff;cursor:pointer;box-shadow:var(--shadow);
  transition:transform .08s ease,filter .15s ease}
.btn:active{transform:scale(.98)} .btn:hover{filter:brightness(1.08)}
.btn-blue{background:linear-gradient(135deg,var(--blue1),var(--blue2))}
.btn-green{background:linear-gradient(135deg,var(--green1),var(--green2))}
.btn-red{background:linear-gradient(135deg,var(--red1),var(--red2))}
.btn-gold{background:linear-gradient(135deg,#f59e0b,#fbbf24);color:#1a1a1a}
.btn-dark{background:linear-gradient(135deg,#1f2937,#374151)}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.row{display:flex;gap:10px;margin-top:10px}
.row .btn{flex:1}
.platform{justify-content:flex-start;padding-right:18px;font-size:17px}
.platform .ico{width:34px;height:34px;border-radius:10px;background:rgba(255,255,255,.18);display:grid;place-items:center;font-size:20px}
.badge{margin-inline-start:auto;background:rgba(0,0,0,.25);padding:4px 10px;border-radius:999px;font-size:13px;font-weight:600}
.country{justify-content:flex-start;padding-right:14px}
.flag{font-size:22px;margin-inline-end:6px}
h2{margin:6px 4px 12px;font-size:18px}
.num{font-family:ui-monospace,Menlo,Consolas,monospace;background:#0d1426;border:1px dashed #2a3a5f;border-radius:12px;
  padding:14px;text-align:center;font-size:18px;letter-spacing:1px;margin:8px 0;color:#a7f3d0}
.toast{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);background:#111a2e;border:1px solid #2a3a5f;
  padding:10px 16px;border-radius:999px;font-size:14px;opacity:0;transition:opacity .25s;z-index:99}
.toast.show{opacity:1}
.empty{padding:24px;text-align:center;color:var(--muted)}
.stats{display:flex;gap:8px;justify-content:space-between}
.stat{flex:1;background:#0d1426;border-radius:12px;padding:10px;text-align:center}
.stat b{display:block;font-size:18px;color:#22c55e}
</style></head><body>
<div class="app">
  <div class="header">
    <div class="logo">🦊</div>
    <div><div class="title">FOX Bot Number</div><div class="sub">Mini App — Live Numbers & OTP</div></div>
  </div>
  <div id="view"></div>
</div>
<div id="toast" class="toast"></div>
<script>
const tg = window.Telegram?.WebApp; if(tg){ tg.expand(); tg.ready(); tg.setHeaderColor('#0b1220'); }
const initData = tg?.initData || '';
const view = document.getElementById('view');
const toastEl = document.getElementById('toast');
function toast(t){ toastEl.textContent=t; toastEl.classList.add('show'); setTimeout(()=>toastEl.classList.remove('show'),1800); }
async function api(path, params={}){
  const url = new URL(location.origin + path);
  Object.entries(params).forEach(([k,v])=>url.searchParams.set(k,v));
  const r = await fetch(url, {headers:{'X-Init-Data':initData}});
  return r.json();
}
function copy(t){ navigator.clipboard.writeText(t).then(()=>toast('✅ Copied: '+t)); tg?.HapticFeedback?.impactOccurred('light'); }

async function home(){
  const me = await api('/api/me');
  view.innerHTML = `
    <div class="card">
      <div class="stats">
        <div class="stat"><b>${me.balance.toFixed(4)}</b><span>💲 Balance</span></div>
        <div class="stat"><b>${me.total_received}</b><span>📥 Received</span></div>
        <div class="stat"><b>${me.live}</b><span>🟢 Live</span></div>
      </div>
    </div>
    <div class="card">
      <button class="btn btn-blue" onclick="platforms()">📱 GET NUMBER</button>
      <div class="row">
        <button class="btn btn-green" onclick="leaderboard()">🏆 LEADERBOARD</button>
        <button class="btn btn-gold" onclick="window.open('${window.GROUP||"#"}','_blank')">✈️ OTPL Group</button>
      </div>
    </div>`;
}

async function platforms(){
  const d = await api('/api/platforms');
  view.innerHTML = `<h2>🎭 Choose the platform</h2><div class="card">` +
    d.items.map(p=>`<button class="btn platform" style="background:linear-gradient(135deg,${p.color},#0ea5e9);margin-bottom:8px"
      onclick="countries('${p.id}')">
      <span class="ico">${p.emoji}</span><span>${p.name}</span><span class="badge">${p.count}</span></button>`).join('') +
    `<button class="btn btn-red" onclick="home()">↩️ Back to Main</button></div>`;
}

async function countries(pid){
  const d = await api('/api/countries', {platform:pid});
  if(!d.items.length){
    view.innerHTML = `<h2>🌐 Choose Country</h2>
      <div class="card"><div class="empty">⚠️ لا توجد أرقام متاحة لهذه المنصة الآن.</div>
      <button class="btn btn-red" onclick="platforms()">🔙 Back To Services</button></div>`; return;
  }
  const items = d.items.map((c,i)=>{
    const cls = (i%2===0)?'btn-blue':'btn-green';
    return `<button class="btn country ${cls}" onclick="getNumbers('${pid}','${c.code}')">
      <span class="flag">${c.flag}</span>${c.en} (+${c.code}) <span class="badge">${c.count}</span></button>`;
  });
  // grid 2 cols
  let grid = '<div class="grid">' + items.join('') + '</div>';
  view.innerHTML = `<h2>🌐 Choose Country for ${d.platform.emoji} ${d.platform.name}</h2>
    <div class="card">${grid}<div style="height:8px"></div>
      <button class="btn btn-red" onclick="platforms()">🔙 Back To Services</button></div>`;
}

async function getNumbers(pid, cc){
  const d = await api('/api/give', {platform:pid, cc:cc});
  if(d.error){ toast('⚠️ '+d.error); return; }
  const nums = d.numbers.map(n=>`<div class="num" onclick="copy('+${n}')">📋 +${n}</div>`).join('');
  view.innerHTML = `<h2>${d.flag} ${d.platform.emoji} ${d.platform.name} — ${d.ar} (+${cc})</h2>
    <div class="card">${nums}
      <div class="row">
        <button class="btn btn-blue" onclick="getNumbers('${pid}','${cc}')">🔄 Change Number</button>
        <button class="btn btn-green" onclick="countries('${pid}')">🌍 Change Country</button>
      </div>
      <div style="height:8px"></div>
      <button class="btn btn-red" onclick="home()">↩️ Back to Main</button>
    </div>`;
  tg?.HapticFeedback?.notificationOccurred('success');
}

async function leaderboard(){
  const d = await api('/api/leaderboard');
  const rows = d.items.map((r,i)=>`<button class="btn ${i===0?'btn-gold':(i%2?'btn-blue':'btn-green')}" style="justify-content:space-between;margin-bottom:6px">
    <span>${['🥇','🥈','🥉'][i]||('#'+(i+1))} ${r.name}</span><span class="badge">${r.total}</span></button>`).join('');
  view.innerHTML = `<h2>🏆 LEADERBOARD</h2><div class="card">${rows||'<div class="empty">لا بيانات</div>'}
    <button class="btn btn-red" onclick="home()">↩️ Back to Main</button></div>`;
}

window.GROUP = "__GROUP__";
home();
</script></body></html>"""


@app.route("/")
def index():
    return Response(INDEX_HTML.replace("__GROUP__", GROUP_LINK), mimetype="text/html")


@app.route("/api/me")
def api_me():
    u = get_user_from_request()
    if not u: return jsonify({"error":"unauthorized"}), 401
    conn = db()
    conn.execute("INSERT OR IGNORE INTO users(user_id,username,first_name) VALUES (?,?,?)",
                 (u["id"], u.get("username",""), u.get("first_name","")))
    conn.commit()
    row = conn.execute("SELECT balance,total_received FROM users WHERE user_id=?", (u["id"],)).fetchone()
    live = conn.execute("SELECT COUNT(*) FROM numbers WHERE status='free'").fetchone()[0]
    conn.close()
    return jsonify({"balance": row["balance"], "total_received": row["total_received"], "live": live})


@app.route("/api/platforms")
def api_platforms():
    if not get_user_from_request(): return jsonify({"error":"unauthorized"}),401
    conn = db(); out = []
    for pid, p in PLATFORMS.items():
        cnt = conn.execute("SELECT COUNT(*) FROM numbers WHERE platform=? AND status='free'", (pid,)).fetchone()[0]
        out.append({"id":pid, "name":p["name"], "emoji":p["emoji"], "color":p["color"], "count":cnt})
    conn.close()
    return jsonify({"items": out})


@app.route("/api/countries")
def api_countries():
    if not get_user_from_request(): return jsonify({"error":"unauthorized"}),401
    pid = request.args.get("platform","")
    p = PLATFORMS.get(pid)
    if not p: return jsonify({"error":"bad platform"}),400
    conn = db()
    rows = conn.execute("""SELECT country_code, COUNT(*) cnt FROM numbers
                           WHERE platform=? AND status='free'
                           GROUP BY country_code ORDER BY cnt DESC""", (pid,)).fetchall()
    conn.close()
    items = []
    for r in rows:
        en, ar, fl = COUNTRY_MAP.get(r["country_code"], ("Unknown","غير معروف","🏳️"))
        items.append({"code":r["country_code"],"en":en,"ar":ar,"flag":fl,"count":r["cnt"]})
    return jsonify({"platform":{"id":pid,"name":p["name"],"emoji":p["emoji"]}, "items":items})


@app.route("/api/give")
def api_give():
    u = get_user_from_request()
    if not u: return jsonify({"error":"unauthorized"}),401
    pid = request.args.get("platform"); cc = request.args.get("cc")
    p = PLATFORMS.get(pid)
    if not p: return jsonify({"error":"bad platform"}),400
    conn = db()
    rows = conn.execute("""SELECT * FROM numbers WHERE platform=? AND country_code=? AND status='free'
                           ORDER BY id LIMIT ?""", (pid, cc, NUMBERS_PER_REQUEST)).fetchall()
    if not rows: conn.close(); return jsonify({"error":"لا توجد أرقام متاحة"})
    ids = [r["id"] for r in rows]
    conn.execute(f"""UPDATE numbers SET status='given', assigned_to=?, assigned_at=datetime('now')
                     WHERE id IN ({','.join('?'*len(ids))})""", [u["id"], *ids])
    conn.commit(); conn.close()
    en, ar, fl = COUNTRY_MAP.get(cc, ("Unknown","غير معروف","🏳️"))
    return jsonify({"numbers":[r["number"] for r in rows], "en":en, "ar":ar, "flag":fl,
                    "platform":{"id":pid,"name":p["name"],"emoji":p["emoji"]}})


@app.route("/api/leaderboard")
def api_leaderboard():
    if not get_user_from_request(): return jsonify({"error":"unauthorized"}),401
    conn = db()
    rows = conn.execute("""SELECT first_name,total_received FROM users
                           ORDER BY total_received DESC LIMIT 10""").fetchall()
    conn.close()
    return jsonify({"items":[{"name":r["first_name"] or "User","total":r["total_received"]} for r in rows]})


# ============================================================
# Telegram bot (opens the WebApp)
# ============================================================
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


@bot.message_handler(commands=["start"])
def cmd_start(m):
    conn = db()
    conn.execute("INSERT OR IGNORE INTO users(user_id,username,first_name) VALUES (?,?,?)",
                 (m.from_user.id, m.from_user.username or "", m.from_user.first_name or ""))
    conn.commit(); conn.close()
    try: bot.send_sticker(m.chat.id, WELCOME_STICKER_ID)
    except: pass
    # زر يفتح الـ WebApp (مطلوب https)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("🚀 Open FOX App", web_app=types.WebAppInfo(url=WEBAPP_URL)))
    bot.send_message(m.chat.id,
        "👋 <b>WELCOME!</b>\nThis is <b>FOX Bot Number</b>.\n\n"
        "اضغط الزر بالأسفل لفتح التطبيق المصغّر 🚀", reply_markup=kb)


@bot.message_handler(commands=["admin"])
def cmd_admin(m):
    if m.from_user.id not in ADMIN_IDS: return
    msg = bot.send_message(m.chat.id,
        "أرسل الأرقام بالشكل:\n<code>platform|number</code> سطر لكل رقم\n"
        f"المنصات: {', '.join(PLATFORMS.keys())}")
    bot.register_next_step_handler(msg, admin_add)


def admin_add(m):
    if m.from_user.id not in ADMIN_IDS: return
    added = 0; conn = db()
    for line in (m.text or "").splitlines():
        if "|" not in line: continue
        plat, num = [x.strip() for x in line.split("|",1)]
        if plat not in PLATFORMS: plat = "other"
        num = re.sub(r"\D","",num)
        if len(num) < 7: continue
        cc, *_ = detect_country(num)
        try:
            conn.execute("INSERT INTO numbers(platform,country_code,number) VALUES (?,?,?)",
                         (plat, cc, num)); added += 1
        except sqlite3.IntegrityError: pass
    conn.commit(); conn.close()
    bot.reply_to(m, f"✅ أُضيف {added} رقم")


# ============================================================
# Fetcher → push OTPs to user via Telegram message
# ============================================================
def fetcher_loop():
    while True:
        try:
            for item in panel.fetch_sms():
                num, sms = item["number"], item["sms"]
                code = extract_code(sms)
                if not code: continue
                hk = hash_key(num, code)
                conn = db()
                if conn.execute("SELECT 1 FROM otps WHERE hash_key=?", (hk,)).fetchone():
                    conn.close(); continue
                cc, en, ar, fl = detect_country(num)
                platform = detect_platform(sms)
                row = conn.execute("""SELECT assigned_to FROM numbers
                                      WHERE number=? AND status='given'""", (num,)).fetchone()
                target = row["assigned_to"] if row else None
                conn.execute("""INSERT INTO otps(platform,country_code,number,code,full_sms,hash_key,delivered_to)
                                VALUES (?,?,?,?,?,?,?)""",
                             (platform, cc, num, code, sms, hk, target))
                if target:
                    conn.execute("""UPDATE users SET balance=balance+?, total_received=total_received+1
                                    WHERE user_id=?""", (REWARD_PER_OTP, target))
                    bal = conn.execute("SELECT balance FROM users WHERE user_id=?", (target,)).fetchone()["balance"]
                    conn.execute("UPDATE numbers SET status='used' WHERE number=?", (num,))
                    pemoji = PLATFORMS.get(platform, PLATFORMS["other"])["emoji"]
                    txt = (f"🌐 <b>Country:</b> {ar} {fl} - {pemoji}\n"
                           f"☎️ <b>Number:</b> <code>{num}</code>\n"
                           f"🔑 <b>OTP Code:</b> <code>{code}</code>\n"
                           f"🏆  -&gt; Reward: {REWARD_PER_OTP:.4f}\n"
                           f"💲  -&gt; Balance: {bal:.4f}")
                    try: bot.send_message(target, txt)
                    except Exception as e: log.warning(f"send: {e}")
                conn.commit(); conn.close()
        except Exception as e:
            log.error(f"fetcher: {e}")
        time.sleep(FETCH_INTERVAL)


# ============================================================
# Entrypoint
# ============================================================
def run_flask():
    log.info(f"Web server → http://{WEB_HOST}:{WEB_PORT}  (WebApp URL: {WEBAPP_URL})")
    app.run(host=WEB_HOST, port=WEB_PORT, debug=False, use_reloader=False, threaded=True)


def main():
    init_db()
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=fetcher_loop, daemon=True).start()
    log.info("Bot polling …")
    bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=25)


if __name__ == "__main__":
    main()
