# -*- coding: utf-8 -*-
"""
FOX Bot Number — Telegram bot
=============================
Connects to a Zyron / IVASMS-style panel ( http://151.80.19.204/ints/ )
and distributes phone numbers + OTPs to users, grouped by platform & country.

Style inspired by the screenshots provided:
- /start welcome with animated sticker (logo)
- "Choose the platform" menu (Facebook / WhatsApp / IMO / TikTok / Instagram ...)
- Each platform has its own pool (folder) of numbers
- Choose Country (auto-detects ANY country in the world from the +code)
- User receives 4 numbers at once (not just one)
- OTP delivery format identical to the screenshot:
    🌐 Country: <name> <flag> - <platform-emoji>
    ☎️ Number: <number>
    🔑 OTP Code: <code>
    🏆 -> Reward: 0.0030
    💲 -> Balance: <balance>
  ( No site name written under the code. )

Requirements:
    pip install pyTelegramBotAPI requests beautifulsoup4

Edit the CONFIG block below, then:
    python fox_bot.py
"""

import os
import re
import time
import json
import html
import sqlite3
import threading
import logging
from datetime import datetime
from typing import Optional, List, Dict, Tuple

import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types

# ============================================================
# CONFIG  — غيّر هذه القيم فقط
# ============================================================
BOT_TOKEN      = "8794957674:AAHzev14d5JM7F3IpOQaCn-J_hRNSuGVrn8"
ADMIN_IDS      = [8761832730]               # ضع آيدي الأدمن(ات)
SITE_BASE      = "http://151.80.19.204/ints"
SITE_USERNAME  = "Hama11"
SITE_PASSWORD  = "Hama11"
GROUP_LINK     = "https://t.me/+IaUh8c8vXnIzYTM0" # رابط مجموعة OTPL
REWARD_PER_OTP = 0.0030
NUMBERS_PER_REQUEST = 4                    # كم رقم يُعطى للمستخدم بكل طلب
FETCH_INTERVAL = 8                         # ثواني بين كل سحب من الموقع
DB_PATH        = "fox_bot.db"

# ملصق متحرك (لوغو حركي) — استبدله بـ file_id لملصقك إن أردت
WELCOME_STICKER_ID = "CAACAgIAAxkBAAEBQYZl4n5hWfQ"  # مثال؛ غيره

# ============================================================
# Platforms / Services  (كل منصة = مجلد منفصل)
# ============================================================
PLATFORMS = {
    "facebook":  {"name": "Facebook",  "emoji": "📘", "keywords": ["facebook", "fb", "meta"]},
    "whatsapp":  {"name": "WhatsApp",  "emoji": "🟢", "keywords": ["whatsapp", "whats app", "wa"]},
    "imo":       {"name": "IMO",       "emoji": "🌟", "keywords": ["imo"]},
    "tiktok":    {"name": "TikTok",    "emoji": "🎵", "keywords": ["tiktok", "tik tok"]},
    "instagram": {"name": "Instagram", "emoji": "📸", "keywords": ["instagram", "insta", "ig"]},
    "telegram":  {"name": "Telegram",  "emoji": "✈️", "keywords": ["telegram", "tg"]},
    "google":    {"name": "Google",    "emoji": "🔎", "keywords": ["google", "gmail"]},
    "twitter":   {"name": "Twitter/X", "emoji": "🐦", "keywords": ["twitter", " x ", "x.com"]},
    "other":     {"name": "Other",     "emoji": "🗂️", "keywords": []},
}

# ============================================================
# COUNTRY DATABASE  — يعرف كل دولة في العالم (ITU dialing codes)
# الشكل: dialing_code -> (English Name, Arabic Name, Flag)
# نُرتّب بالأطول أولاً لمطابقة 1xxx بدقة.
# ============================================================
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
    ("353","Ireland","أيرلندا","🇮🇪"),("972","Israel/Palestine","فلسطين","🇵🇸"),
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
# نرتب من الأطول للأقصر لضمان مطابقة الأكواد الطويلة (مثل 1264) قبل (1)
COUNTRIES_SORTED = sorted(COUNTRIES_RAW, key=lambda x: -len(x[0]))


def detect_country(number: str) -> Tuple[str, str, str, str]:
    """يكتشف الدولة من الرقم. يعيد (code, en_name, ar_name, flag)"""
    num = re.sub(r"\D", "", number or "")
    for code, en, ar, flag in COUNTRIES_SORTED:
        if num.startswith(code):
            return code, en, ar, flag
    return "?", "Unknown", "غير معروف", "🏳️"


# ============================================================
# Logging
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("fox-bot")


# ============================================================
# Database
# ============================================================
def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    c = db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        balance REAL DEFAULT 0,
        total_received INTEGER DEFAULT 0,
        banned INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS numbers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT,
        country_code TEXT,
        number TEXT UNIQUE,
        status TEXT DEFAULT 'free',   -- free | given | used
        assigned_to INTEGER,
        assigned_at TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS otps(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT,
        country_code TEXT,
        number TEXT,
        code TEXT,
        full_sms TEXT,
        hash_key TEXT UNIQUE,
        delivered_to INTEGER,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_num_pool ON numbers(platform, country_code, status);
    """)
    c.commit()
    c.close()


# ============================================================
# Zyron / IVASMS panel client
# ============================================================
class PanelClient:
    def __init__(self, base, user, pwd):
        self.base = base.rstrip("/")
        self.user = user
        self.pwd = pwd
        self.s = requests.Session()
        self.s.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        })
        self.logged_in = False
        self.lock = threading.Lock()

    def _solve_captcha(self, html_text: str) -> Optional[str]:
        # موقع IVASMS أحيانًا يطلب: "Solve : 3 + 5"
        m = re.search(r"(\d+)\s*([\+\-\*])\s*(\d+)", html_text)
        if not m:
            return None
        a, op, b = int(m.group(1)), m.group(2), int(m.group(3))
        return str({"+": a+b, "-": a-b, "*": a*b}[op])

    def login(self) -> bool:
        try:
            r = self.s.get(f"{self.base}/login", timeout=20)
            soup = BeautifulSoup(r.text, "html.parser")
            token_el = soup.find("input", {"name": "_token"})
            token = token_el["value"] if token_el else ""
            captcha = self._solve_captcha(r.text) or ""
            data = {
                "_token": token,
                "email": self.user,
                "password": self.pwd,
                "capt": captcha,
            }
            r2 = self.s.post(f"{self.base}/signin", data=data,
                             headers={"Referer": f"{self.base}/login"},
                             timeout=20, allow_redirects=True)
            self.logged_in = ("logout" in r2.text.lower()
                              or "dashboard" in r2.url.lower()
                              or "client" in r2.url.lower())
            log.info(f"Login -> {self.logged_in} ({r2.status_code})")
            return self.logged_in
        except Exception as e:
            log.error(f"Login error: {e}")
            return False

    def fetch_sms(self) -> List[Dict]:
        """يجلب آخر الرسائل من data_smscdr.php"""
        with self.lock:
            if not self.logged_in and not self.login():
                return []
            url = f"{self.base}/client/res/data_smscdr.php"
            today = datetime.utcnow().strftime("%Y-%m-%d")
            params = {
                "fdate1": f"{today} 00:00:00",
                "fdate2": f"{today} 23:59:59",
                "frange": "", "fclient": "", "fnum": "",
                "fcli": "", "fgdate": "", "fgmonth": "",
                "fgrange": "", "fgclient": "", "fgnumber": "",
                "fgcli": "", "fg": "0",
                "iDisplayStart": 0, "iDisplayLength": 50,
            }
            try:
                r = self.s.get(url, params=params, timeout=20, headers={
                    "Referer": f"{self.base}/client/SMSCDRStats",
                    "X-Requested-With": "XMLHttpRequest",
                })
                if r.status_code == 401 or "login" in r.url:
                    self.logged_in = False
                    self.login()
                    return []
                data = r.json()
                out = []
                for row in data.get("aaData", []):
                    # شكل الصف يختلف حسب اللوحة؛ نحاول استخراج رقم + رسالة
                    cells = [BeautifulSoup(str(c), "html.parser").get_text(" ", strip=True)
                             for c in row]
                    joined = " | ".join(cells)
                    num_m = re.search(r"(\+?\d{8,15})", joined)
                    sms = cells[-1] if cells else ""
                    if not num_m:
                        continue
                    out.append({
                        "number": num_m.group(1).lstrip("+"),
                        "sms": sms,
                        "raw": joined,
                    })
                return out
            except Exception as e:
                log.error(f"fetch_sms error: {e}")
                self.logged_in = False
                return []


panel = PanelClient(SITE_BASE, SITE_USERNAME, SITE_PASSWORD)


# ============================================================
# Helpers
# ============================================================
OTP_REGEX = re.compile(r"(\b\d{3}[- ]?\d{3,4}\b|\b\d{4,8}\b)")


def extract_code(sms: str) -> Optional[str]:
    m = OTP_REGEX.search(sms or "")
    return m.group(1) if m else None


def detect_platform(sms: str) -> str:
    s = (sms or "").lower()
    for pid, p in PLATFORMS.items():
        if pid == "other":
            continue
        for kw in p["keywords"]:
            if kw in s:
                return pid
    return "other"


def hash_key(number: str, code: str) -> str:
    return f"{number}:{code}"


# ============================================================
# Bot
# ============================================================
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


def ensure_user(msg) -> sqlite3.Row:
    c = db()
    u = msg.from_user
    c.execute("INSERT OR IGNORE INTO users(user_id, username, first_name) VALUES (?,?,?)",
              (u.id, u.username or "", u.first_name or ""))
    c.commit()
    row = c.execute("SELECT * FROM users WHERE user_id=?", (u.id,)).fetchone()
    c.close()
    return row


def is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


# ----------------- Keyboards -----------------
def kb_main():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("📱  GET NUMBER", callback_data="get"))
    kb.add(types.InlineKeyboardButton("🟢  LIVE TRAFFIC", callback_data="live"),
           types.InlineKeyboardButton("🏆  LEADERBOARD", callback_data="lb"))
    kb.add(types.InlineKeyboardButton("💰  BALANCE", callback_data="bal"),
           types.InlineKeyboardButton("👥  GROUP",     url=GROUP_LINK))
    return kb


def kb_platforms():
    kb = types.InlineKeyboardMarkup(row_width=1)
    c = db()
    for pid, p in PLATFORMS.items():
        cnt = c.execute("SELECT COUNT(*) FROM numbers WHERE platform=? AND status='free'",
                        (pid,)).fetchone()[0]
        kb.add(types.InlineKeyboardButton(
            f"{p['emoji']}  {p['name']}  ({cnt})", callback_data=f"plat:{pid}"))
    c.close()
    kb.add(types.InlineKeyboardButton("⬅️  Back to Main", callback_data="main"))
    return kb


def kb_countries(platform: str):
    c = db()
    rows = c.execute("""SELECT country_code, COUNT(*) cnt FROM numbers
                        WHERE platform=? AND status='free'
                        GROUP BY country_code ORDER BY cnt DESC""", (platform,)).fetchall()
    c.close()
    kb = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for r in rows:
        cc = r["country_code"]
        info = next(((en, ar, fl) for code, en, ar, fl in COUNTRIES_SORTED if code == cc),
                    ("Unknown", "غير معروف", "🏳️"))
        en, ar, fl = info
        buttons.append(types.InlineKeyboardButton(
            f"{fl} {en} (+{cc})  · {r['cnt']}",
            callback_data=f"cn:{platform}:{cc}"))
    for i in range(0, len(buttons), 2):
        kb.row(*buttons[i:i+2])
    kb.add(types.InlineKeyboardButton("🔙  Back To Services", callback_data="get"))
    return kb


def kb_after_numbers(platform, cc):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("🔄 Change Number", callback_data=f"cn:{platform}:{cc}"),
           types.InlineKeyboardButton("🌍 Change Country", callback_data=f"plat:{platform}"))
    kb.add(types.InlineKeyboardButton("✈️ OTPL Group", url=GROUP_LINK))
    kb.add(types.InlineKeyboardButton("↩️ Back to Main", callback_data="main"))
    return kb


# ----------------- Handlers -----------------
WELCOME = (
    "👋 <b>WELCOME!</b>\n"
    "This is <b>[FOX Bot Number]</b>.\n\n"
    "🧭 <b>PLEASE SELECT A BUTTON BELOW:</b>\n"
    "• 📱  GET NUMBER\n"
    "• 🟢  LIVE TRAFFIC\n"
    "• 🏆  LEADERBOARD\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "💡 Tap a button above\n"
    "📌 Your activity will be tracked\n"
    "✨ Enjoy FOX Bot Number! 🚀"
)


@bot.message_handler(commands=["start"])
def cmd_start(m):
    ensure_user(m)
    # لوغو حركية
    try:
        bot.send_sticker(m.chat.id, WELCOME_STICKER_ID)
    except Exception:
        pass
    bot.send_message(m.chat.id, WELCOME, reply_markup=kb_main())


@bot.callback_query_handler(func=lambda c: True)
def on_cb(c: types.CallbackQuery):
    data = c.data
    uid = c.from_user.id
    ensure_user(c.message)

    if data == "main":
        bot.edit_message_text(WELCOME, c.message.chat.id, c.message.message_id,
                              reply_markup=kb_main())
        return

    if data == "get":
        bot.edit_message_text("🎭 <b>Choose the platform:</b>",
                              c.message.chat.id, c.message.message_id,
                              reply_markup=kb_platforms())
        return

    if data.startswith("plat:"):
        pid = data.split(":")[1]
        p = PLATFORMS.get(pid)
        bot.edit_message_text(f"🌐 <b>Choose Country for</b> {p['emoji']} {p['name']}",
                              c.message.chat.id, c.message.message_id,
                              reply_markup=kb_countries(pid))
        return

    if data.startswith("cn:"):
        _, pid, cc = data.split(":")
        give_numbers(c, pid, cc)
        return

    if data == "bal":
        row = db().execute("SELECT balance,total_received FROM users WHERE user_id=?",
                           (uid,)).fetchone()
        bot.answer_callback_query(c.id,
            f"💰 Balance: {row['balance']:.4f}\n📥 Numbers: {row['total_received']}",
            show_alert=True)
        return

    if data == "lb":
        rows = db().execute("""SELECT first_name, total_received FROM users
                               ORDER BY total_received DESC LIMIT 10""").fetchall()
        txt = "🏆 <b>LEADERBOARD</b>\n\n"
        for i, r in enumerate(rows, 1):
            txt += f"{i}. {html.escape(r['first_name'] or 'User')} — {r['total_received']}\n"
        bot.edit_message_text(txt, c.message.chat.id, c.message.message_id,
                              reply_markup=kb_main())
        return

    if data == "live":
        cnt = db().execute("SELECT COUNT(*) FROM numbers WHERE status='free'").fetchone()[0]
        bot.answer_callback_query(c.id, f"🟢 LIVE: {cnt} free numbers", show_alert=True)


def give_numbers(c, platform, cc):
    uid = c.from_user.id
    conn = db()
    rows = conn.execute("""SELECT * FROM numbers
                           WHERE platform=? AND country_code=? AND status='free'
                           ORDER BY id LIMIT ?""",
                        (platform, cc, NUMBERS_PER_REQUEST)).fetchall()
    if not rows:
        bot.answer_callback_query(c.id, "⚠️ لا توجد أرقام متاحة الآن.", show_alert=True)
        conn.close()
        return
    ids = [r["id"] for r in rows]
    conn.execute(f"""UPDATE numbers SET status='given', assigned_to=?,
                     assigned_at=datetime('now')
                     WHERE id IN ({','.join('?'*len(ids))})""", [uid, *ids])
    conn.commit()

    info = next(((en, ar, fl) for code, en, ar, fl in COUNTRIES_SORTED if code == cc),
                ("Unknown", "غير معروف", "🏳️"))
    en, ar, fl = info
    pemoji = PLATFORMS[platform]["emoji"]
    pname  = PLATFORMS[platform]["name"]

    kb = types.InlineKeyboardMarkup(row_width=1)
    text = f"{fl} <b>{pname}</b> — {ar}  (+{cc})\n\n"
    for r in rows:
        text += f"📋  <code>+{r['number']}</code>\n"
    bot.send_message(c.message.chat.id, text, reply_markup=kb_after_numbers(platform, cc))
    bot.answer_callback_query(c.id, f"✅ تم تسليم {len(rows)} أرقام")
    conn.close()


# ============================================================
# Admin
# ============================================================
@bot.message_handler(commands=["admin"])
def cmd_admin(m):
    if not is_admin(m.from_user.id):
        return
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("➕ Add numbers (paste)", callback_data="adm:add"))
    kb.add(types.InlineKeyboardButton("📊 Stats", callback_data="adm:stats"))
    kb.add(types.InlineKeyboardButton("🧹 Clear used", callback_data="adm:clear"))
    bot.send_message(m.chat.id, "👑 <b>Admin Panel</b>", reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data.startswith("adm:"))
def on_admin(c):
    if not is_admin(c.from_user.id):
        return
    a = c.data.split(":")[1]
    if a == "stats":
        conn = db()
        u = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        n = conn.execute("SELECT COUNT(*) FROM numbers").fetchone()[0]
        f = conn.execute("SELECT COUNT(*) FROM numbers WHERE status='free'").fetchone()[0]
        o = conn.execute("SELECT COUNT(*) FROM otps").fetchone()[0]
        conn.close()
        bot.answer_callback_query(c.id, f"👥 {u}  📞 {n} (free {f})  🔑 {o}", show_alert=True)
    elif a == "add":
        msg = bot.send_message(c.message.chat.id,
            "أرسل الأرقام بالشكل:\n<code>platform|number</code> سطر لكل رقم\n"
            f"المنصات: {', '.join(PLATFORMS.keys())}")
        bot.register_next_step_handler(msg, admin_add_numbers)
    elif a == "clear":
        db().execute("DELETE FROM numbers WHERE status='used'")
        db().commit()
        bot.answer_callback_query(c.id, "🧹 تم", show_alert=True)


def admin_add_numbers(m):
    if not is_admin(m.from_user.id):
        return
    added = 0
    conn = db()
    for line in (m.text or "").splitlines():
        line = line.strip()
        if "|" not in line:
            continue
        plat, num = [x.strip() for x in line.split("|", 1)]
        if plat not in PLATFORMS:
            plat = "other"
        num = re.sub(r"\D", "", num)
        if len(num) < 7:
            continue
        cc, *_ = detect_country(num)
        try:
            conn.execute("INSERT INTO numbers(platform,country_code,number) VALUES (?,?,?)",
                         (plat, cc, num))
            added += 1
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()
    bot.reply_to(m, f"✅ أُضيف {added} رقم")


# ============================================================
# Background fetcher — يلتقط OTPs من الموقع ويُسلّمها
# ============================================================
def fetcher_loop():
    while True:
        try:
            messages = panel.fetch_sms()
            for item in messages:
                num = item["number"]
                sms = item["sms"]
                code = extract_code(sms)
                if not code:
                    continue
                hk = hash_key(num, code)
                conn = db()
                # تجنّب التكرار
                exists = conn.execute("SELECT 1 FROM otps WHERE hash_key=?", (hk,)).fetchone()
                if exists:
                    conn.close()
                    continue
                cc, en, ar, fl = detect_country(num)
                platform = detect_platform(sms)
                # ابحث عن من استلم هذا الرقم
                row = conn.execute("""SELECT assigned_to FROM numbers
                                      WHERE number=? AND status='given'""", (num,)).fetchone()
                target = row["assigned_to"] if row else None
                conn.execute("""INSERT INTO otps(platform,country_code,number,code,
                                full_sms,hash_key,delivered_to)
                                VALUES (?,?,?,?,?,?,?)""",
                             (platform, cc, num, code, sms, hk, target))
                if target:
                    conn.execute("""UPDATE users SET balance=balance+?,
                                    total_received=total_received+1
                                    WHERE user_id=?""", (REWARD_PER_OTP, target))
                    bal = conn.execute("SELECT balance FROM users WHERE user_id=?",
                                       (target,)).fetchone()["balance"]
                    conn.execute("UPDATE numbers SET status='used' WHERE number=?", (num,))
                    conn.commit()
                    pemoji = PLATFORMS.get(platform, PLATFORMS["other"])["emoji"]
                    # تنسيق التسليم — مطابق للصورة (بدون اسم الموقع)
                    txt = (
                        f"🌐 <b>Country:</b> {ar} {fl} - {pemoji}\n"
                        f"☎️ <b>Number:</b> <code>{num}</code>\n"
                        f"🔑 <b>OTP Code:</b> <code>{code}</code>\n"
                        f"🏆  -&gt; Reward: {REWARD_PER_OTP:.4f}\n"
                        f"💲  -&gt; Balance: {bal:.4f}"
                    )
                    try:
                        bot.send_message(target, txt)
                    except Exception as e:
                        log.warning(f"send to {target} failed: {e}")
                conn.commit()
                conn.close()
        except Exception as e:
            log.error(f"fetcher: {e}")
        time.sleep(FETCH_INTERVAL)


# ============================================================
# Main
# ============================================================
def main():
    init_db()
    threading.Thread(target=fetcher_loop, daemon=True).start()
    log.info("Bot running …")
    bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=25)


if __name__ == "__main__":
    main()
