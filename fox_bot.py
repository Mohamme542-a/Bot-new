#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================
  Abu Ibrahim Al-Muhajir  |  OTP Telegram Bot  (Single File)
================================================================
Features
--------
* Login to Zyron/IVASMS panel (auto math captcha solver).
* Multi-platform routing (Facebook / WhatsApp / IMO / TikTok / Instagram / Telegram / Google / Twitter / Signal ...).
* Auto country detection for ANY country in the world via E.164 prefix table (built-in, ~240 countries).
* Each user gets up to 4 private numbers, never shared with other users.
* If no OTP arrives in 5 minutes -> number auto-released back to pool.
* If OTP arrives -> number is permanently removed from the bot.
* Admin: upload combo file (txt/csv), add/delete numbers, stats, broadcast,
  ban/unban, reset balances, view users.
* SQLite (WAL) with proper indexes + atomic allocation (prevents duplicates).
* Pro UI buttons in green/blue (Telegram InlineKeyboard layout matching screenshots).
* OTP message formatting matches the provided screenshot exactly.

Run
---
    pip install pyTelegramBotAPI requests beautifulsoup4 lxml
    python abu_ibrahim_bot.py

Edit the CONFIG block below (BOT_TOKEN, ADMIN_IDS, PANEL_*).
"""

import os, re, sys, time, json, html, queue, sqlite3, logging, threading, traceback
from io import BytesIO
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types

# ============================================================
#                       CONFIG
# ============================================================
BOT_TOKEN   = os.getenv("BOT_TOKEN",   "8919284673:AAEsKk8mYpqS-NjHmARr5eX5KaCq95zzcFQ")
ADMIN_IDS   = [int(x) for x in os.getenv("ADMIN_IDS", "8761832730").split(",") if x.strip()]

PANEL_URL   = os.getenv("PANEL_URL",   "http://151.80.19.204/ints/login")  # or your Zyron URL
PANEL_USER  = os.getenv("PANEL_USER",  "Hama11")
PANEL_PASS  = os.getenv("PANEL_PASS",  "Hama11")

GROUP_LINK  = os.getenv("GROUP_LINK",  "https://t.me/+IaUh8c8vXnIzYTM0")
DB_PATH     = os.getenv("DB_PATH",     "abu_ibrahim.db")

MAX_NUMBERS_PER_USER = 4
HOLD_MINUTES         = 5         # auto-release if no OTP in 5 min
REWARD_PER_OTP       = 0.0030    # matches screenshot
FETCH_INTERVAL_SEC   = 8         # how often we poll the panel

# Default platforms (admin can add more via combo upload)
DEFAULT_PLATFORMS = [
    ("facebook",  "📘 Facebook"),
    ("whatsapp",  "🟢 WhatsApp"),
    ("imo",       "🌟 IMO"),
    ("tiktok",    "🎵 TikTok"),
    ("instagram", "📸 Instagram"),
    ("telegram",  "✈️ Telegram"),
    ("google",    "🔵 Google"),
    ("twitter",   "🐦 Twitter/X"),
    ("signal",    "🔒 Signal"),
    ("other",     "🌐 Other"),
]

# ============================================================
#                       LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler("bot.log", encoding="utf-8")],
)
log = logging.getLogger("AbuIbrahim")

# ============================================================
#       COUNTRY TABLE  (E.164 prefixes -> Name + Flag + AR)
# ============================================================
# Sorted longest-prefix-first so detection picks the most specific match.
COUNTRIES_RAW = [
    # code,  EN,                AR,                  flag
    ("1242","Bahamas","الباهاما","🇧🇸"),("1246","Barbados","بربادوس","🇧🇧"),
    ("1264","Anguilla","أنغويلا","🇦🇮"),("1268","Antigua and Barbuda","أنتيغوا وبربودا","🇦🇬"),
    ("1284","British Virgin Islands","جزر العذراء البريطانية","🇻🇬"),("1340","US Virgin Islands","جزر العذراء الأمريكية","🇻🇮"),
    ("1345","Cayman Islands","جزر كايمان","🇰🇾"),("1441","Bermuda","برمودا","🇧🇲"),
    ("1473","Grenada","غرينادا","🇬🇩"),("1649","Turks and Caicos","تركس وكايكوس","🇹🇨"),
    ("1664","Montserrat","مونتسيرات","🇲🇸"),("1670","Northern Mariana Islands","ماريانا الشمالية","🇲🇵"),
    ("1671","Guam","غوام","🇬🇺"),("1684","American Samoa","ساموا الأمريكية","🇦🇸"),
    ("1721","Sint Maarten","سينت مارتن","🇸🇽"),("1758","Saint Lucia","سانت لوسيا","🇱🇨"),
    ("1767","Dominica","دومينيكا","🇩🇲"),("1784","Saint Vincent","سانت فنسنت","🇻🇨"),
    ("1787","Puerto Rico","بورتوريكو","🇵🇷"),("1809","Dominican Republic","الدومينيكان","🇩🇴"),
    ("1829","Dominican Republic","الدومينيكان","🇩🇴"),("1849","Dominican Republic","الدومينيكان","🇩🇴"),
    ("1868","Trinidad and Tobago","ترينيداد وتوباغو","🇹🇹"),("1869","Saint Kitts","سانت كيتس","🇰🇳"),
    ("1876","Jamaica","جامايكا","🇯🇲"),("1939","Puerto Rico","بورتوريكو","🇵🇷"),
    ("7",   "Russia","روسيا","🇷🇺"),
    ("20",  "Egypt","مصر","🇪🇬"),
    ("212", "Morocco","المغرب","🇲🇦"),("213","Algeria","الجزائر","🇩🇿"),
    ("216", "Tunisia","تونس","🇹🇳"),("218","Libya","ليبيا","🇱🇾"),
    ("220", "Gambia","غامبيا","🇬🇲"),("221","Senegal","السنغال","🇸🇳"),
    ("222", "Mauritania","موريتانيا","🇲🇷"),("223","Mali","مالي","🇲🇱"),
    ("224", "Guinea","غينيا","🇬🇳"),("225","Ivory Coast","ساحل العاج","🇨🇮"),
    ("226", "Burkina Faso","بوركينا فاسو","🇧🇫"),("227","Niger","النيجر","🇳🇪"),
    ("228", "Togo","توغو","🇹🇬"),("229","Benin","بنين","🇧🇯"),
    ("230", "Mauritius","موريشيوس","🇲🇺"),("231","Liberia","ليبيريا","🇱🇷"),
    ("232", "Sierra Leone","سيراليون","🇸🇱"),("233","Ghana","غانا","🇬🇭"),
    ("234", "Nigeria","نيجيريا","🇳🇬"),("235","Chad","تشاد","🇹🇩"),
    ("236", "Central African Republic","أفريقيا الوسطى","🇨🇫"),("237","Cameroon","الكاميرون","🇨🇲"),
    ("238", "Cape Verde","الرأس الأخضر","🇨🇻"),("239","Sao Tome","ساو تومي","🇸🇹"),
    ("240", "Equatorial Guinea","غينيا الاستوائية","🇬🇶"),("241","Gabon","الغابون","🇬🇦"),
    ("242", "Congo","الكونغو","🇨🇬"),("243","DR Congo","الكونغو الديمقراطية","🇨🇩"),
    ("244", "Angola","أنغولا","🇦🇴"),("245","Guinea-Bissau","غينيا بيساو","🇬🇼"),
    ("246", "Diego Garcia","دييغو غارسيا","🇮🇴"),("248","Seychelles","سيشل","🇸🇨"),
    ("249", "Sudan","السودان","🇸🇩"),("250","Rwanda","رواندا","🇷🇼"),
    ("251", "Ethiopia","إثيوبيا","🇪🇹"),("252","Somalia","الصومال","🇸🇴"),
    ("253", "Djibouti","جيبوتي","🇩🇯"),("254","Kenya","كينيا","🇰🇪"),
    ("255", "Tanzania","تنزانيا","🇹🇿"),("256","Uganda","أوغندا","🇺🇬"),
    ("257", "Burundi","بوروندي","🇧🇮"),("258","Mozambique","موزمبيق","🇲🇿"),
    ("260", "Zambia","زامبيا","🇿🇲"),("261","Madagascar","مدغشقر","🇲🇬"),
    ("262", "Reunion","لا ريونيون","🇷🇪"),("263","Zimbabwe","زيمبابوي","🇿🇼"),
    ("264", "Namibia","ناميبيا","🇳🇦"),("265","Malawi","مالاوي","🇲🇼"),
    ("266", "Lesotho","ليسوتو","🇱🇸"),("267","Botswana","بوتسوانا","🇧🇼"),
    ("268", "Eswatini","إسواتيني","🇸🇿"),("269","Comoros","جزر القمر","🇰🇲"),
    ("27",  "South Africa","جنوب أفريقيا","🇿🇦"),
    ("290", "Saint Helena","سانت هيلينا","🇸🇭"),("291","Eritrea","إريتريا","🇪🇷"),
    ("297", "Aruba","أروبا","🇦🇼"),("298","Faroe Islands","جزر فارو","🇫🇴"),
    ("299", "Greenland","غرينلاند","🇬🇱"),
    ("30",  "Greece","اليونان","🇬🇷"),("31","Netherlands","هولندا","🇳🇱"),
    ("32",  "Belgium","بلجيكا","🇧🇪"),("33","France","فرنسا","🇫🇷"),
    ("34",  "Spain","إسبانيا","🇪🇸"),("36","Hungary","المجر","🇭🇺"),
    ("39",  "Italy","إيطاليا","🇮🇹"),
    ("350", "Gibraltar","جبل طارق","🇬🇮"),("351","Portugal","البرتغال","🇵🇹"),
    ("352", "Luxembourg","لوكسمبورغ","🇱🇺"),("353","Ireland","أيرلندا","🇮🇪"),
    ("354", "Iceland","آيسلندا","🇮🇸"),("355","Albania","ألبانيا","🇦🇱"),
    ("356", "Malta","مالطا","🇲🇹"),("357","Cyprus","قبرص","🇨🇾"),
    ("358", "Finland","فنلندا","🇫🇮"),("359","Bulgaria","بلغاريا","🇧🇬"),
    ("370", "Lithuania","ليتوانيا","🇱🇹"),("371","Latvia","لاتفيا","🇱🇻"),
    ("372", "Estonia","إستونيا","🇪🇪"),("373","Moldova","مولدوفا","🇲🇩"),
    ("374", "Armenia","أرمينيا","🇦🇲"),("375","Belarus","بيلاروسيا","🇧🇾"),
    ("376", "Andorra","أندورا","🇦🇩"),("377","Monaco","موناكو","🇲🇨"),
    ("378", "San Marino","سان مارينو","🇸🇲"),("380","Ukraine","أوكرانيا","🇺🇦"),
    ("381", "Serbia","صربيا","🇷🇸"),("382","Montenegro","الجبل الأسود","🇲🇪"),
    ("383", "Kosovo","كوسوفو","🇽🇰"),("385","Croatia","كرواتيا","🇭🇷"),
    ("386", "Slovenia","سلوفينيا","🇸🇮"),("387","Bosnia","البوسنة","🇧🇦"),
    ("389", "North Macedonia","مقدونيا الشمالية","🇲🇰"),
    ("40",  "Romania","رومانيا","🇷🇴"),("41","Switzerland","سويسرا","🇨🇭"),
    ("420", "Czech Republic","التشيك","🇨🇿"),("421","Slovakia","سلوفاكيا","🇸🇰"),
    ("423", "Liechtenstein","ليختنشتاين","🇱🇮"),
    ("43",  "Austria","النمسا","🇦🇹"),("44","United Kingdom","المملكة المتحدة","🇬🇧"),
    ("45",  "Denmark","الدنمارك","🇩🇰"),("46","Sweden","السويد","🇸🇪"),
    ("47",  "Norway","النرويج","🇳🇴"),("48","Poland","بولندا","🇵🇱"),
    ("49",  "Germany","ألمانيا","🇩🇪"),
    ("500", "Falkland","فوكلاند","🇫🇰"),("501","Belize","بليز","🇧🇿"),
    ("502", "Guatemala","غواتيمالا","🇬🇹"),("503","El Salvador","السلفادور","🇸🇻"),
    ("504", "Honduras","هندوراس","🇭🇳"),("505","Nicaragua","نيكاراغوا","🇳🇮"),
    ("506", "Costa Rica","كوستاريكا","🇨🇷"),("507","Panama","بنما","🇵🇦"),
    ("508", "Saint Pierre","سان بيير","🇵🇲"),("509","Haiti","هايتي","🇭🇹"),
    ("51",  "Peru","البيرو","🇵🇪"),("52","Mexico","المكسيك","🇲🇽"),
    ("53",  "Cuba","كوبا","🇨🇺"),("54","Argentina","الأرجنتين","🇦🇷"),
    ("55",  "Brazil","البرازيل","🇧🇷"),("56","Chile","تشيلي","🇨🇱"),
    ("57",  "Colombia","كولومبيا","🇨🇴"),("58","Venezuela","فنزويلا","🇻🇪"),
    ("590", "Guadeloupe","غوادلوب","🇬🇵"),("591","Bolivia","بوليفيا","🇧🇴"),
    ("592", "Guyana","غيانا","🇬🇾"),("593","Ecuador","الإكوادور","🇪🇨"),
    ("594", "French Guiana","غويانا الفرنسية","🇬🇫"),("595","Paraguay","الباراغواي","🇵🇾"),
    ("596", "Martinique","مارتينيك","🇲🇶"),("597","Suriname","سورينام","🇸🇷"),
    ("598", "Uruguay","الأوروغواي","🇺🇾"),
    ("60",  "Malaysia","ماليزيا","🇲🇾"),("61","Australia","أستراليا","🇦🇺"),
    ("62",  "Indonesia","إندونيسيا","🇮🇩"),("63","Philippines","الفلبين","🇵🇭"),
    ("64",  "New Zealand","نيوزيلندا","🇳🇿"),("65","Singapore","سنغافورة","🇸🇬"),
    ("66",  "Thailand","تايلاند","🇹🇭"),
    ("670", "Timor-Leste","تيمور الشرقية","🇹🇱"),("672","Norfolk","نورفولك","🇳🇫"),
    ("673", "Brunei","بروناي","🇧🇳"),("674","Nauru","ناورو","🇳🇷"),
    ("675", "Papua New Guinea","بابوا غينيا","🇵🇬"),("676","Tonga","تونغا","🇹🇴"),
    ("677", "Solomon Islands","جزر سليمان","🇸🇧"),("678","Vanuatu","فانواتو","🇻🇺"),
    ("679", "Fiji","فيجي","🇫🇯"),("680","Palau","بالاو","🇵🇼"),
    ("681", "Wallis","واليس","🇼🇫"),("682","Cook Islands","جزر كوك","🇨🇰"),
    ("683", "Niue","نيوي","🇳🇺"),("685","Samoa","ساموا","🇼🇸"),
    ("686", "Kiribati","كيريباتي","🇰🇮"),("687","New Caledonia","كاليدونيا","🇳🇨"),
    ("688", "Tuvalu","توفالو","🇹🇻"),("689","French Polynesia","بولينيزيا","🇵🇫"),
    ("690", "Tokelau","توكيلاو","🇹🇰"),("691","Micronesia","ميكرونيزيا","🇫🇲"),
    ("692", "Marshall Islands","جزر مارشال","🇲🇭"),
    ("81",  "Japan","اليابان","🇯🇵"),("82","South Korea","كوريا الجنوبية","🇰🇷"),
    ("84",  "Vietnam","فيتنام","🇻🇳"),
    ("850", "North Korea","كوريا الشمالية","🇰🇵"),("852","Hong Kong","هونغ كونغ","🇭🇰"),
    ("853", "Macau","ماكاو","🇲🇴"),("855","Cambodia","كمبوديا","🇰🇭"),
    ("856", "Laos","لاوس","🇱🇦"),("86","China","الصين","🇨🇳"),
    ("880", "Bangladesh","بنغلاديش","🇧🇩"),("886","Taiwan","تايوان","🇹🇼"),
    ("90",  "Turkey","تركيا","🇹🇷"),("91","India","الهند","🇮🇳"),
    ("92",  "Pakistan","باكستان","🇵🇰"),("93","Afghanistan","أفغانستان","🇦🇫"),
    ("94",  "Sri Lanka","سريلانكا","🇱🇰"),("95","Myanmar","ميانمار","🇲🇲"),
    ("960", "Maldives","المالديف","🇲🇻"),("961","Lebanon","لبنان","🇱🇧"),
    ("962", "Jordan","الأردن","🇯🇴"),("963","Syria","سوريا","🇸🇾"),
    ("964", "Iraq","العراق","🇮🇶"),("965","Kuwait","الكويت","🇰🇼"),
    ("966", "Saudi Arabia","السعودية","🇸🇦"),("967","Yemen","اليمن","🇾🇪"),
    ("968", "Oman","عمان","🇴🇲"),("970","Palestine","فلسطين","🇵🇸"),
    ("971", "UAE","الإمارات","🇦🇪"),("972","Israel","إسرائيل","🇮🇱"),
    ("973", "Bahrain","البحرين","🇧🇭"),("974","Qatar","قطر","🇶🇦"),
    ("975", "Bhutan","بوتان","🇧🇹"),("976","Mongolia","منغوليا","🇲🇳"),
    ("977", "Nepal","نيبال","🇳🇵"),("98","Iran","إيران","🇮🇷"),
    ("992", "Tajikistan","طاجيكستان","🇹🇯"),("993","Turkmenistan","تركمانستان","🇹🇲"),
    ("994", "Azerbaijan","أذربيجان","🇦🇿"),("995","Georgia","جورجيا","🇬🇪"),
    ("996", "Kyrgyzstan","قيرغيزستان","🇰🇬"),("998","Uzbekistan","أوزبكستان","🇺🇿"),
    ("1",   "USA/Canada","أمريكا/كندا","🇺🇸"),  # last (shortest, fallback)
]
# sort longest first
COUNTRIES = sorted(COUNTRIES_RAW, key=lambda x: -len(x[0]))

def detect_country(number: str):
    """Return (code, en_name, ar_name, flag) for any phone in the world."""
    n = re.sub(r"\D", "", number or "")
    for code, en, ar, flag in COUNTRIES:
        if n.startswith(code):
            return code, en, ar, flag
    return "?", "Unknown", "غير معروف", "🏳️"

# ============================================================
#                       DATABASE
# ============================================================
_db_lock = threading.RLock()

def db():
    if not hasattr(_local, "conn"):
        c = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA synchronous=NORMAL")
        c.row_factory = sqlite3.Row
        _local.conn = c
    return _local.conn

_local = threading.local()

def db_init():
    c = db()
    cur = c.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        username TEXT, first_name TEXT,
        balance REAL DEFAULT 0,
        otps INTEGER DEFAULT 0,
        banned INTEGER DEFAULT 0,
        joined_at TEXT,
        last_seen TEXT
    );
    CREATE TABLE IF NOT EXISTS numbers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT NOT NULL,
        number   TEXT NOT NULL,
        country_code TEXT,
        status TEXT DEFAULT 'free',   -- free / held / used
        holder_id INTEGER,
        held_until TEXT,
        added_at TEXT,
        UNIQUE(platform, number)
    );
    CREATE INDEX IF NOT EXISTS idx_num_lookup ON numbers(platform, country_code, status);
    CREATE INDEX IF NOT EXISTS idx_num_holder ON numbers(holder_id, status);
    CREATE TABLE IF NOT EXISTS platforms(
        key TEXT PRIMARY KEY,
        label TEXT
    );
    CREATE TABLE IF NOT EXISTS settings(
        k TEXT PRIMARY KEY, v TEXT
    );
    """)
    for k, label in DEFAULT_PLATFORMS:
        cur.execute("INSERT OR IGNORE INTO platforms(key,label) VALUES(?,?)", (k, label))
    c.commit()

def now_iso(): return datetime.now(timezone.utc).isoformat()

def upsert_user(u):
    c = db()
    c.execute("""INSERT INTO users(user_id,username,first_name,joined_at,last_seen)
                 VALUES(?,?,?,?,?)
                 ON CONFLICT(user_id) DO UPDATE SET username=excluded.username,
                    first_name=excluded.first_name, last_seen=excluded.last_seen""",
              (u.id, u.username or "", u.first_name or "", now_iso(), now_iso()))
    c.commit()

def is_banned(uid):
    r = db().execute("SELECT banned FROM users WHERE user_id=?", (uid,)).fetchone()
    return bool(r and r["banned"])

# ============================================================
#                  PANEL CLIENT (Zyron / IVASMS)
# ============================================================
class Panel:
    """عميل لوحة Zyron - يحل الكابتشا الحسابي تلقائياً."""
    LOGIN_PATH = "/login"
    SIGNIN_PATH = "/signin"
    STATS_PATH = "/agent/SMSCDRStats"
    DATA_PATH  = "/agent/res/data_smscdr.php"

    def __init__(self, base, user, pwd):
        self.base = base.rstrip("/")
        self.user, self.pwd = user, pwd
        self.s = requests.Session()
        self.s.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        })
        self.logged_in = False
        self.lock = threading.Lock()

    @staticmethod
    def _solve_math(text):  # <--- لاحظ: لا توجد مسافات بادئة قبل def
        """حل كابتشا حسابية مثل: What is 3 + 4 = ? أو 5 - 2"""
        m = re.search(r"(\d+)\s*([\+\-\*xX×])\s*(\d+)", text or "")
        if not m: return None
        a, op, b = int(m.group(1)), m.group(2), int(m.group(3))
        if op == "+": return a + b
        if op == "-": return a - b
        if op in ("*", "x", "X", "×"): return a * b
        return None

    def login(self):
        # ... باقي الكود كما هو ...
        with self.lock:
            try:
                r = self.s.get(f"{PANEL_URL}/login", timeout=20)
                soup = BeautifulSoup(r.text, "lxml")
                token = ""
                t = soup.find("input", {"name": "_token"})
                if t: token = t.get("value", "")
                capt = self._solve_math(soup.get_text(" ", strip=True))
                data = {"_token": token, "email": PANEL_USER, "password": PANEL_PASS}
                if capt is not None: data["capt"] = str(capt); data["captcha"] = str(capt)
                r2 = self.s.post(f"{PANEL_URL}/login", data=data, timeout=20, allow_redirects=True)
                self.logged_in = ("logout" in r2.text.lower()) or (r2.url.endswith("/portal") or "dashboard" in r2.url.lower())
                log.info("Panel login: %s", "OK" if self.logged_in else "FAILED")
                return self.logged_in
            except Exception as e:
                log.error("Panel login error: %s", e)
                self.logged_in = False
                return False

    def fetch_sms(self):
        """Get latest SMS rows from data_smscdr.php style endpoint."""
        if not self.logged_in and not self.login(): return []
        try:
            url = f"{PANEL_URL}/portal/sms/received/getsms"
            today = datetime.utcnow().strftime("%Y-%m-%d")
            r = self.s.post(url, data={"fdate1": today, "fdate2": today}, timeout=20,
                headers={"Referer": f"{PANEL_URL}/portal/sms/received",
                         "X-Requested-With": "XMLHttpRequest"})
            if r.status_code in (401, 403) or "login" in r.url.lower():
                self.logged_in = False; self.login(); return []
            try:    data = r.json()
            except: data = []
            return data if isinstance(data, list) else data.get("aaData", [])
        except Exception as e:
            log.warning("fetch_sms err: %s", e); return []

panel = Panel()

# ============================================================
#                  OTP EXTRACTION
# ============================================================
OTP_PATTERNS = [
    r"\b(\d{3}[-\s]\d{3,4})\b",         # 123-456 or 123 4567
    r"\b(\d{4}[-\s]\d{4})\b",           # 1234-5678
    r"(?<!\d)(\d{4,8})(?!\d)",          # plain 4..8 digit code
]
def extract_otp(text):
    if not text: return None
    # Strip phone numbers (10+ digits) so we don't grab them
    cleaned = re.sub(r"\+?\d{10,}", " ", text)
    for pat in OTP_PATTERNS:
        m = re.search(pat, cleaned)
        if m: return m.group(1)
    return None

# ============================================================
#                  BOT  +  KEYBOARDS
# ============================================================
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML", threaded=True)

def kb_main(is_admin=False):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("📱 Get Number", callback_data="m:get"),
           types.InlineKeyboardButton("🟢 Live Traffic", callback_data="m:live"))
    kb.add(types.InlineKeyboardButton("🏆 Leaderboard", callback_data="m:lb"),
           types.InlineKeyboardButton("💰 My Balance", callback_data="m:bal"))
    kb.add(types.InlineKeyboardButton("📞 My Numbers", callback_data="m:mine"),
           types.InlineKeyboardButton("ℹ️ Help", callback_data="m:help"))
    kb.add(types.InlineKeyboardButton("✈️ OTPL Group", url=GROUP_LINK))
    if is_admin:
        kb.add(types.InlineKeyboardButton("⚙️ Admin Panel", callback_data="adm:home"))
    return kb

def kb_platforms():
    c = db()
    rows = c.execute("""
        SELECT p.key, p.label, COUNT(n.id) cnt
        FROM platforms p
        LEFT JOIN numbers n ON n.platform=p.key AND n.status='free'
        GROUP BY p.key ORDER BY p.label""").fetchall()
    kb = types.InlineKeyboardMarkup(row_width=1)
    for r in rows:
        kb.add(types.InlineKeyboardButton(f"{r['label']} ({r['cnt']})",
                                          callback_data=f"pl:{r['key']}"))
    kb.add(types.InlineKeyboardButton("⬅️ Back", callback_data="m:home"))
    return kb

def kb_countries(platform):
    rows = db().execute("""SELECT country_code, COUNT(*) cnt FROM numbers
                           WHERE platform=? AND status='free'
                           GROUP BY country_code ORDER BY cnt DESC""", (platform,)).fetchall()
    kb = types.InlineKeyboardMarkup(row_width=2)
    btns = []
    for r in rows:
        cc = r["country_code"] or "?"
        _, en, ar, flag = detect_country(cc + "0000000000")
        btns.append(types.InlineKeyboardButton(f"{flag} {en} (+{cc}) · {r['cnt']}",
                                               callback_data=f"co:{platform}:{cc}"))
    # 2 per row
    for i in range(0, len(btns), 2):
        kb.row(*btns[i:i+2])
    kb.add(types.InlineKeyboardButton("⬅️ Back To Services", callback_data="m:get"))
    return kb

def kb_my_numbers(uid, platform=None, country=None):
    q = "SELECT id,number,country_code FROM numbers WHERE holder_id=? AND status='held'"
    args = [uid]
    rows = db().execute(q, args).fetchall()
    kb = types.InlineKeyboardMarkup(row_width=1)
    for r in rows:
        _, en, ar, flag = detect_country(r["number"])
        kb.add(types.InlineKeyboardButton(f"{flag} 📋 +{r['number']}",
                                          callback_data=f"cp:{r['id']}"))
    row = []
    if platform:
        row.append(types.InlineKeyboardButton("🔄 Change Number",
                    callback_data=f"co:{platform}:{country or ''}"))
        row.append(types.InlineKeyboardButton("🌍 Change Country",
                    callback_data=f"pl:{platform}"))
    if row: kb.row(*row)
    kb.add(types.InlineKeyboardButton("✈️ OTPL Group", url=GROUP_LINK))
    kb.add(types.InlineKeyboardButton("↩️ Back to Main", callback_data="m:home"))
    return kb

# ============================================================
#                  HANDLERS
# ============================================================
WELCOME = (
    "👋 <b>WELCOME!</b>\n"
    "This is <b>Abu Ibrahim Al-Muhajir | OTP Bot</b>.\n\n"
    "🧭 <b>Please select a button below:</b>\n"
    "• 📱 Get Number\n"
    "• 🟢 Live Traffic\n"
    "• 🏆 Leaderboard\n\n"
    "💡 Tap a button above\n"
    "📌 Your activity will be tracked\n"
    "✨ Enjoy! 🚀"
)

@bot.message_handler(commands=["start"])
def cmd_start(m):
    upsert_user(m.from_user)
    if is_banned(m.from_user.id):
        return bot.reply_to(m, "🚫 You are banned.")
    bot.send_message(m.chat.id, WELCOME, reply_markup=kb_main(m.from_user.id in ADMIN_IDS))

@bot.message_handler(commands=["help"])
def cmd_help(m):
    bot.reply_to(m, "Use /start to open the menu.")

# ----- callback router
@bot.callback_query_handler(func=lambda c: True)
def on_cb(c):
    uid = c.from_user.id
    upsert_user(c.from_user)
    if is_banned(uid):
        return bot.answer_callback_query(c.id, "🚫 Banned.", show_alert=True)
    data = c.data or ""
    try:
        if data == "m:home":
            bot.edit_message_text(WELCOME, c.message.chat.id, c.message.message_id,
                                  reply_markup=kb_main(uid in ADMIN_IDS))
        elif data == "m:get":
            bot.edit_message_text("🎭 <b>Choose the platform:</b>",
                c.message.chat.id, c.message.message_id, reply_markup=kb_platforms())
        elif data.startswith("pl:"):
            pl = data.split(":",1)[1]
            label = db().execute("SELECT label FROM platforms WHERE key=?", (pl,)).fetchone()
            label = label["label"] if label else pl
            bot.edit_message_text(f"🌍 <b>Choose Country for {label}</b>",
                c.message.chat.id, c.message.message_id, reply_markup=kb_countries(pl))
        elif data.startswith("co:"):
            _, pl, cc = data.split(":", 2)
            allocate_for_user(c, pl, cc)
        elif data.startswith("cp:"):
            nid = int(data.split(":",1)[1])
            r = db().execute("SELECT number FROM numbers WHERE id=?", (nid,)).fetchone()
            if r: bot.answer_callback_query(c.id, f"+{r['number']}", show_alert=True)
        elif data == "m:bal":
            r = db().execute("SELECT balance,otps FROM users WHERE user_id=?", (uid,)).fetchone()
            bot.answer_callback_query(c.id,
                f"💰 Balance: {r['balance']:.4f}\n🔑 OTPs: {r['otps']}", show_alert=True)
        elif data == "m:lb":
            rows = db().execute("SELECT first_name,otps,balance FROM users ORDER BY otps DESC LIMIT 10").fetchall()
            txt = "🏆 <b>Leaderboard</b>\n\n"
            for i,r in enumerate(rows,1):
                txt += f"{i}. {html.escape(r['first_name'] or '?')} — {r['otps']} OTPs ({r['balance']:.4f})\n"
            bot.edit_message_text(txt or "No data", c.message.chat.id, c.message.message_id,
                                  reply_markup=kb_main(uid in ADMIN_IDS))
        elif data == "m:live":
            cnt = db().execute("SELECT COUNT(*) c FROM numbers WHERE status='free'").fetchone()["c"]
            held = db().execute("SELECT COUNT(*) c FROM numbers WHERE status='held'").fetchone()["c"]
            bot.answer_callback_query(c.id, f"🟢 Free: {cnt}\n🟡 Held: {held}", show_alert=True)
        elif data == "m:mine":
            rows = db().execute("SELECT number FROM numbers WHERE holder_id=? AND status='held'",(uid,)).fetchall()
            if not rows:
                bot.answer_callback_query(c.id, "You have no active numbers.", show_alert=True)
            else:
                txt = "📞 <b>Your active numbers:</b>\n\n" + "\n".join(f"• +{r['number']}" for r in rows)
                bot.edit_message_text(txt, c.message.chat.id, c.message.message_id,
                                      reply_markup=kb_my_numbers(uid))
        elif data == "m:help":
            bot.answer_callback_query(c.id,
                f"You can hold up to {MAX_NUMBERS_PER_USER} numbers.\n"
                f"If no OTP in {HOLD_MINUTES} min the number is auto-released.",
                show_alert=True)
        elif data.startswith("adm:") and uid in ADMIN_IDS:
            admin_cb(c, data[4:])
        else:
            bot.answer_callback_query(c.id)
    except Exception as e:
        log.error("cb error: %s\n%s", e, traceback.format_exc())
        try: bot.answer_callback_query(c.id, "Error.")
        except: pass

# ----- allocation (atomic, per-user uniqueness)
_alloc_lock = threading.Lock()
def allocate_for_user(c, platform, country):
    uid = c.from_user.id
    with _alloc_lock:
        c_db = db()
        held = c_db.execute(
          "SELECT COUNT(*) cnt FROM numbers WHERE holder_id=? AND status='held'",(uid,)).fetchone()["cnt"]
        if held >= MAX_NUMBERS_PER_USER:
            return bot.answer_callback_query(c.id,
              f"⚠️ Limit reached ({MAX_NUMBERS_PER_USER}). Wait or release one.",
              show_alert=True)
        row = c_db.execute("""SELECT id,number FROM numbers
            WHERE platform=? AND country_code=? AND status='free'
            ORDER BY RANDOM() LIMIT 1""", (platform, country)).fetchone()
        if not row:
            return bot.answer_callback_query(c.id, "❌ No free numbers for this country.", show_alert=True)
        until = (datetime.now(timezone.utc) + timedelta(minutes=HOLD_MINUTES)).isoformat()
        c_db.execute("""UPDATE numbers SET status='held', holder_id=?, held_until=?
                        WHERE id=? AND status='free'""", (uid, until, row["id"]))
        c_db.commit()
    bot.edit_message_text(
        f"✅ <b>Number reserved for you</b>\n\n"
        f"📞 <code>+{row['number']}</code>\n"
        f"⏱ Hold: {HOLD_MINUTES} min — auto-release if no OTP.",
        c.message.chat.id, c.message.message_id,
        reply_markup=kb_my_numbers(uid, platform, country))

# ============================================================
#                  ADMIN PANEL
# ============================================================
def kb_admin():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("📤 Upload Combo", callback_data="adm:upload"),
           types.InlineKeyboardButton("📊 Stats", callback_data="adm:stats"))
    kb.add(types.InlineKeyboardButton("👥 Users", callback_data="adm:users"),
           types.InlineKeyboardButton("📣 Broadcast", callback_data="adm:bcast"))
    kb.add(types.InlineKeyboardButton("🚫 Ban", callback_data="adm:ban"),
           types.InlineKeyboardButton("✅ Unban", callback_data="adm:unban"))
    kb.add(types.InlineKeyboardButton("💰 Reset Balance", callback_data="adm:reset"),
           types.InlineKeyboardButton("🗑 Clear Numbers", callback_data="adm:clear"))
    kb.add(types.InlineKeyboardButton("➕ Add Platform", callback_data="adm:addpl"),
           types.InlineKeyboardButton("⬅️ Back", callback_data="m:home"))
    return kb

_pending_action = {}  # uid -> action

def admin_cb(c, action):
    uid = c.from_user.id
    if action == "home":
        return bot.edit_message_text("⚙️ <b>Admin Panel</b>", c.message.chat.id, c.message.message_id,
                                     reply_markup=kb_admin())
    if action == "stats":
        d = db()
        u = d.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
        n = d.execute("SELECT COUNT(*) c FROM numbers").fetchone()["c"]
        f = d.execute("SELECT COUNT(*) c FROM numbers WHERE status='free'").fetchone()["c"]
        h = d.execute("SELECT COUNT(*) c FROM numbers WHERE status='held'").fetchone()["c"]
        us = d.execute("SELECT COUNT(*) c FROM numbers WHERE status='used'").fetchone()["c"]
        bot.edit_message_text(
            f"📊 <b>Stats</b>\n👥 Users: {u}\n📞 Numbers: {n}\n🟢 Free: {f}\n🟡 Held: {h}\n✅ Used: {us}",
            c.message.chat.id, c.message.message_id, reply_markup=kb_admin())
        return
    if action == "upload":
        _pending_action[uid] = ("upload", None)
        bot.send_message(c.message.chat.id,
            "📤 Send a combo file (.txt/.csv).\n"
            "Format per line: <code>platform|number</code>\n"
            "Example: <code>facebook|962779296870</code>\n"
            "Country is detected automatically.")
        return
    if action == "bcast":
        _pending_action[uid] = ("bcast", None)
        bot.send_message(c.message.chat.id, "📣 Send the broadcast text now.")
        return
    if action in ("ban","unban","reset"):
        _pending_action[uid] = (action, None)
        bot.send_message(c.message.chat.id, f"Send the user_id to <b>{action}</b>.")
        return
    if action == "clear":
        db().execute("DELETE FROM numbers WHERE status='free'"); db().commit()
        bot.answer_callback_query(c.id, "Free numbers cleared.", show_alert=True)
        return
    if action == "addpl":
        _pending_action[uid] = ("addpl", None)
        bot.send_message(c.message.chat.id, "Send: <code>key|Label with emoji</code>")
        return
    if action == "users":
        rows = db().execute("SELECT user_id,first_name,otps,balance,banned FROM users ORDER BY otps DESC LIMIT 20").fetchall()
        txt = "👥 <b>Top users</b>\n\n" + "\n".join(
            f"{'🚫' if r['banned'] else '✅'} <code>{r['user_id']}</code> "
            f"{html.escape(r['first_name'] or '')} — {r['otps']} OTPs / {r['balance']:.4f}"
            for r in rows)
        bot.edit_message_text(txt or "No users.", c.message.chat.id, c.message.message_id,
                              reply_markup=kb_admin())
        return

@bot.message_handler(content_types=["document"])
def on_doc(m):
    if m.from_user.id not in ADMIN_IDS: return
    act = _pending_action.get(m.from_user.id)
    if not act or act[0] != "upload": return
    try:
        f = bot.get_file(m.document.file_id)
        data = bot.download_file(f.file_path).decode("utf-8", errors="ignore")
    except Exception as e:
        return bot.reply_to(m, f"Read error: {e}")
    added = skipped = 0
    c = db()
    for ln in data.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"): continue
        # accept "platform|number" OR just "number" (defaults to 'other')
        if "|" in ln:
            pl, num = ln.split("|", 1)
        else:
            pl, num = "other", ln
        pl = pl.strip().lower()
        num = re.sub(r"\D", "", num)
        if not num or len(num) < 7: skipped += 1; continue
        code, *_ = detect_country(num)
        # ensure platform exists
        c.execute("INSERT OR IGNORE INTO platforms(key,label) VALUES(?,?)",
                  (pl, f"🌐 {pl.title()}"))
        try:
            c.execute("""INSERT INTO numbers(platform,number,country_code,status,added_at)
                         VALUES(?,?,?,'free',?)""", (pl, num, code, now_iso()))
            added += 1
        except sqlite3.IntegrityError:
            skipped += 1
    c.commit()
    _pending_action.pop(m.from_user.id, None)
    bot.reply_to(m, f"✅ Added: {added}\n⏭ Skipped (dupes/invalid): {skipped}")

@bot.message_handler(func=lambda m: m.from_user.id in ADMIN_IDS and m.from_user.id in _pending_action)
def on_admin_text(m):
    act, _ = _pending_action.pop(m.from_user.id)
    txt = (m.text or "").strip()
    c = db()
    if act == "bcast":
        n = 0
        for r in c.execute("SELECT user_id FROM users WHERE banned=0").fetchall():
            try: bot.send_message(r["user_id"], txt); n += 1
            except: pass
        return bot.reply_to(m, f"📣 Sent to {n} users.")
    if act in ("ban","unban"):
        try: uid = int(txt)
        except: return bot.reply_to(m, "Bad user_id.")
        c.execute("UPDATE users SET banned=? WHERE user_id=?", (1 if act=="ban" else 0, uid))
        c.commit(); return bot.reply_to(m, "Done.")
    if act == "reset":
        try: uid = int(txt)
        except: return bot.reply_to(m, "Bad user_id.")
        c.execute("UPDATE users SET balance=0,otps=0 WHERE user_id=?", (uid,))
        c.commit(); return bot.reply_to(m, "Reset.")
    if act == "addpl":
        if "|" not in txt: return bot.reply_to(m, "Use key|Label")
        k, lbl = txt.split("|",1)
        c.execute("INSERT OR REPLACE INTO platforms(key,label) VALUES(?,?)",(k.strip().lower(), lbl.strip()))
        c.commit(); return bot.reply_to(m, "Platform saved.")

# ============================================================
#                  FETCHER (OTP delivery)
# ============================================================
_delivered_keys = set()  # in-memory dedup

def deliver_otp(num, otp, platform_label="📘 Facebook"):
    c = db()
    row = c.execute("""SELECT id,holder_id,platform FROM numbers
                       WHERE number=? AND status='held'""", (num,)).fetchone()
    if not row: return False
    uid = row["holder_id"]
    code, en, ar, flag = detect_country(num)
    pl_row = c.execute("SELECT label FROM platforms WHERE key=?", (row["platform"],)).fetchone()
    pl_label = pl_row["label"] if pl_row else platform_label
    # delete from bot (per requirement)
    c.execute("DELETE FROM numbers WHERE id=?", (row["id"],))
    # credit user
    c.execute("""UPDATE users SET balance=balance+?, otps=otps+1 WHERE user_id=?""",
              (REWARD_PER_OTP, uid))
    new_bal = c.execute("SELECT balance FROM users WHERE user_id=?", (uid,)).fetchone()["balance"]
    c.commit()
    msg = (
        f"🌐 Country: {ar} {flag} - {pl_label}\n"
        f"☎️ Number: {num}\n"
        f"🔑 OTP Code: {otp}\n"
        f"🏆 - &gt; Reward: {REWARD_PER_OTP:.4f}\n"
        f"💲 - &gt; Balance: {new_bal:.4f}"
    )
    try: bot.send_message(uid, msg)
    except Exception as e: log.warning("send otp fail: %s", e)
    return True

def release_expired():
    c = db()
    now = datetime.now(timezone.utc).isoformat()
    rows = c.execute("SELECT id,holder_id,number FROM numbers WHERE status='held' AND held_until<?",(now,)).fetchall()
    for r in rows:
        c.execute("UPDATE numbers SET status='free', holder_id=NULL, held_until=NULL WHERE id=?", (r["id"],))
        try: bot.send_message(r["holder_id"], f"⌛ +{r['number']} released (no OTP in {HOLD_MINUTES} min).")
        except: pass
    if rows: c.commit()

def fetcher_loop():
    while True:
        try:
            release_expired()
            rows = panel.fetch_sms() or []
            for it in rows:
                # ivasms aaData -> [date, range, number, cli, message, ...]
                if isinstance(it, list) and len(it) >= 5:
                    number = re.sub(r"\D","", str(it[2]))
                    text   = str(it[4])
                elif isinstance(it, dict):
                    number = re.sub(r"\D","", str(it.get("number") or it.get("to") or ""))
                    text   = str(it.get("message") or it.get("sms") or "")
                else: continue
                key = f"{number}:{hash(text)}"
                if key in _delivered_keys: continue
                otp = extract_otp(text)
                if not otp: continue
                if deliver_otp(number, otp):
                    _delivered_keys.add(key)
                    if len(_delivered_keys) > 5000: _delivered_keys.clear()
        except Exception as e:
            log.error("fetcher err: %s", e)
        time.sleep(FETCH_INTERVAL_SEC)

# ============================================================
#                  MAIN
# ============================================================
def main():
    db_init()
    log.info("Logging in to panel...")
    panel.login()
    t = threading.Thread(target=fetcher_loop, daemon=True); t.start()
    log.info("Bot starting polling...")
    bot.infinity_polling(skip_pending=True, timeout=30)

if __name__ == "__main__":
    main()
