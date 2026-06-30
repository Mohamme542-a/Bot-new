import asyncio
import requests
import random
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import re
import html
import time

# --- CONFIG ---
# API 1 & 2 — Token format [sender, number, message, date]
API1_URL   = "http://147.135.212.197/crapi/st/viewstats"
API1_TOKEN = "SE5XREZBUzRfTpVnX2dQh3NQcYB2dZBWQ4JpXVxmblp2alCDi25oZg=="

# API 2 ZENEX — جديد (وضعناه في متغير جديد تماماً)
API2_URL   = "https://api.zenexnetwork.com/v1/numsuccess/info"
API2_TOKEN = "ZNX_KB2H1GOF4PJR4H6FN9GJ1VMX"

# API 3 — pscall format {result, data:[{dateadded,num,cli,sms}]}
API3_URL = "https://pscall.net/restapi/smsreport"
API3_KEY = "SFNYSj1SS16DgYdyf4KIgA=="

BOT_TOKEN   = "8907846587:AAHWEG-2zS8Kr1iTuulE0nYDhhvuDTcch1E"
TARGET_CHAT = '-1003725814394'

bot = Bot(token=BOT_TOKEN)

# --- COUNTRY DATABASE ---
country_db = {
    "1":"🇺🇸 USA/Canada","93":"🇦🇫 Afghanistan","355":"🇦🇱 Albania","213":"🇩🇿 Algeria",
    "376":"🇦🇩 Andorra","244":"🇦🇴 Angola","1264":"🇦🇮 Anguilla","1268":"🇦🇬 Antigua",
    "54":"🇦🇷 Argentina","374":"🇦🇲 Armenia","61":"🇦🇺 Australia","43":"🇦🇹 Austria",
    "994":"🇦🇿 Azerbaijan","1242":"🇧🇸 Bahamas","973":"🇧🇭 Bahrain","880":"🇧🇩 Bangladesh",
    "1246":"🇧🇧 Barbados","375":"🇧🇾 Belarus","32":"🇧🇪 Belgium","501":"🇧🇿 Belize",
    "229":"🇧🇯 Benin","1441":"🇧🇲 Bermuda","975":"🇧🇹 Bhutan","591":"🇧🇴 Bolivia",
    "387":"🇧🇦 Bosnia","267":"🇧🇼 Botswana","55":"🇧🇷 Brazil","673":"🇧🇳 Brunei",
    "359":"🇧🇬 Bulgaria","226":"🇧🇫 Burkina Faso","257":"🇧🇮 Burundi","855":"🇰🇭 Cambodia",
    "237":"🇨🇲 Cameroon","238":"🇨🇻 Cape Verde","1345":"🇰🇾 Cayman Islands",
    "236":"🇨🇫 Central African Republic","235":"🇹🇩 Chad","56":"🇨🇱 Chile","86":"🇨🇳 China",
    "57":"🇨🇴 Colombia","269":"🇰🇲 Comoros","242":"🇨🇬 Republic of Congo",
    "243":"🇨🇩 DR Congo","506":"🇨🇷 Costa Rica","385":"🇭🇷 Croatia","53":"🇨🇺 Cuba",
    "357":"🇨🇾 Cyprus","420":"🇨🇿 Czech Republic","45":"🇩🇰 Denmark","253":"🇩🇯 Djibouti",
    "1767":"🇩🇲 Dominica","1809":"🇩🇴 Dominican Republic","593":"🇪🇨 Ecuador",
    "20":"🇪🇬 Egypt","503":"🇸🇻 El Salvador","240":"🇬🇶 Equatorial Guinea",
    "291":"🇪🇷 Eritrea","372":"🇪🇪 Estonia","251":"🇪🇹 Ethiopia","679":"🇫🇯 Fiji",
    "358":"🇫🇮 Finland","33":"🇫🇷 France","689":"🇵🇫 French Polynesia","241":"🇬🇦 Gabon",
    "220":"🇬🇲 Gambia","995":"🇬🇪 Georgia","49":"🇩🇪 Germany","233":"🇬🇭 Ghana",
    "350":"🇬🇮 Gibraltar","30":"🇬🇷 Greece","1473":"🇬🇩 Grenada","502":"🇬🇹 Guatemala",
    "224":"🇬🇳 Guinea","245":"🇬🇼 Guinea-Bissau","592":"🇬🇾 Guyana","509":"🇭🇹 Haiti",
    "504":"🇭🇳 Honduras","852":"🇭🇰 Hong Kong","36":"🇭🇺 Hungary","354":"🇮🇸 Iceland",
    "91":"🇮🇳 India","62":"🇮🇩 Indonesia","98":"🇮🇷 Iran","964":"🇮🇶 Iraq",
    "353":"🇮🇪 Ireland","972":"🇮🇱 Israel","39":"🇮🇹 Italy","1876":"🇯🇲 Jamaica",
    "81":"🇯🇵 Japan","962":"🇯🇴 Jordan","254":"🇰🇪 Kenya","686":"🇰🇮 Kiribati",
    "965":"🇰🇼 Kuwait","996":"🇰🇬 Kyrgyzstan","856":"🇱🇦 Laos","371":"🇱🇻 Latvia",
    "961":"🇱🇧 Lebanon","266":"🇱🇸 Lesotho","231":"🇱🇷 Liberia","218":"🇱🇾 Libya",
    "370":"🇱🇹 Lithuania","352":"🇱🇺 Luxembourg","853":"🇲🇴 Macau","389":"🇲🇰 Macedonia",
    "261":"🇲🇬 Madagascar","265":"🇲🇼 Malawi","60":"🇲🇾 Malaysia","960":"🇲🇻 Maldives",
    "223":"🇲🇱 Mali","356":"🇲🇹 Malta","692":"🇲🇭 Marshall Islands","222":"🇲🇷 Mauritania",
    "230":"🇲🇺 Mauritius","52":"🇲🇽 Mexico","691":"🇫🇲 Micronesia","373":"🇲🇩 Moldova",
    "377":"🇲🇨 Monaco","976":"🇲🇳 Mongolia","382":"🇲🇪 Montenegro","1664":"🇲🇸 Montserrat",
    "212":"🇲🇦 Morocco","258":"🇲🇿 Mozambique","95":"🇲🇲 Myanmar","264":"🇳🇦 Namibia",
    "674":"🇳🇷 Nauru","977":"🇳🇵 Nepal","31":"🇳🇱 Netherlands","64":"🇳🇿 New Zealand",
    "505":"🇳🇮 Nicaragua","227":"🇳🇪 Niger","234":"🇳🇬 Nigeria","850":"🇰🇵 North Korea",
    "47":"🇳🇴 Norway","968":"🇴🇲 Oman","92":"🇵🇰 Pakistan","680":"🇵🇼 Palau",
    "970":"🇵🇸 Palestine","507":"🇵🇦 Panama","675":"🇵🇬 Papua New Guinea",
    "595":"🇵🇾 Paraguay","51":"🇵🇪 Peru","63":"🇵🇭 Philippines","48":"🇵🇱 Poland",
    "351":"🇵🇹 Portugal","1787":"🇵🇷 Puerto Rico","974":"🇶🇦 Qatar","40":"🇷🇴 Romania",
    "7":"🇷🇺 Russia/Kazakhstan","250":"🇷🇼 Rwanda","685":"🇼🇸 Samoa",
    "239":"🇸🇹 Sao Tome","966":"🇸🇦 Saudi Arabia","221":"🇸🇳 Senegal","381":"🇷🇸 Serbia",
    "248":"🇸🇨 Seychelles","232":"🇸🇱 Sierra Leone","65":"🇸🇬 Singapore",
    "421":"🇸🇰 Slovakia","386":"🇸🇮 Slovenia","677":"🇸🇧 Solomon Islands",
    "252":"🇸🇴 Somalia","27":"🇿🇦 South Africa","82":"🇰🇷 South Korea",
    "211":"🇸🇸 South Sudan","34":"🇪🇸 Spain","94":"🇱🇰 Sri Lanka","249":"🇸🇩 Sudan",
    "597":"🇸🇷 Suriname","268":"🇸🇿 Swaziland","46":"🇸🇪 Sweden","41":"🇨🇭 Switzerland",
    "963":"🇸🇾 Syria","886":"🇹🇼 Taiwan","992":"🇹🇯 Tajikistan","255":"🇹🇿 Tanzania",
    "66":"🇹🇭 Thailand","670":"🇹🇱 Timor-Leste","228":"🇹🇬 Togo","676":"🇹🇴 Tonga",
    "1868":"🇹🇹 Trinidad & Tobago","216":"🇹🇳 Tunisia","90":"🇹🇷 Turkey",
    "993":"🇹🇲 Turkmenistan","1649":"🇹🇨 Turks & Caicos","688":"🇹🇻 Tuvalu",
    "256":"🇺🇬 Uganda","380":"🇺🇦 Ukraine","971":"🇦🇪 UAE","44":"🇬🇧 UK",
    "598":"🇺🇾 Uruguay","998":"🇺🇿 Uzbekistan","678":"🇻🇺 Vanuatu",
    "58":"🇻🇪 Venezuela","84":"🇻🇳 Vietnam","1284":"🇻🇬 British Virgin Islands",
    "1340":"🇻🇮 US Virgin Islands","967":"🇾🇪 Yemen","260":"🇿🇲 Zambia",
    "263":"🇿🇼 Zimbabwe",
    "700":"🇰🇿 Kazakhstan","701":"🇰🇿 Kazakhstan","702":"🇰🇿 Kazakhstan",
    "703":"🇰🇿 Kazakhstan","704":"🇰🇿 Kazakhstan","705":"🇰🇿 Kazakhstan",
    "706":"🇰🇿 Kazakhstan","707":"🇰🇿 Kazakhstan","708":"🇰🇿 Kazakhstan",
    "747":"🇰🇿 Kazakhstan","770":"🇰🇿 Kazakhstan","771":"🇰🇿 Kazakhstan",
    "777":"🇰🇿 Kazakhstan","778":"🇰🇿 Kazakhstan",
    "584":"🇻🇪 Venezuela","582":"🇻🇪 Venezuela","581":"🇻🇪 Venezuela",
}

def get_country(number):
    d = str(number).replace("+","").replace(" ","")
    for l in range(4, 0, -1):
        if d[:l] in country_db:
            return country_db[d[:l]]
    return "🌍 Unknown"

def extract_code(msg):
    match = re.search(r'\b\d{3}[-\s]\d{3}\b|\b\d{4,8}\b', str(msg))
    return match.group(0) if match else "N/A"

# --- SEEN IDs (duplicate rokne ke liye) ---
seen_ids = set()

async def send_sms(service, number, message, date):
    uid = f"{date}|{number}|{message[:30]}"
    if uid in seen_ids:
        return
    seen_ids.add(uid)

    country = get_country(number)
    code    = extract_code(message)
    clean   = str(number).replace("+","")
    masked  = clean[:6] + "****" + clean[-3:] if len(clean) > 7 else clean

    text = (
        f"💐 <b>『 ɴᴇᴡ ᴏᴛᴘ ʀᴇᴄᴇɪᴠᴇᴅ 』</b> ✨\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>⌚ ᴛɪᴍᴇ:</b> <code>{html.escape(str(date))}</code>\n"
        f"<b>🌍 ᴄᴏᴜɴᴛʀʏ:</b> {html.escape(str(country))}\n"
        f"<b>📱 ɴᴜᴍʙᴇʀ:</b> <code>{html.escape(str(masked))}</code>\n"
        f"<b>🛠 ꜱᴇʀᴠɪᴄᴇ:</b> <code>{html.escape(str(service))}</code>\n"
        f"<b>🔑 ᴄᴏᴅᴇ:</b> <code>{html.escape(str(code))}</code>\n\n"
        f"<b>💬 ᴍᴇssᴀɢᴇ:</b>\n<pre>{html.escape(str(message))}</pre>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📱 Channel", url="https://t.me/junaidaliniz"),
            InlineKeyboardButton("☎️ Number",  url="https://t.me/JunaidnnRebot")
        ],
        [
            InlineKeyboardButton("📥 NO. CHNL",  url="https://t.me/junaidaliniz"),
            InlineKeyboardButton("🎀 MAIN CHNL", url="https://t.me/junaidaliniz")
        ]
    ])

    try:
        await bot.send_message(
            chat_id=TARGET_CHAT,
            text=text,
            parse_mode="HTML",
            reply_markup=kb,
            disable_web_page_preview=True
        )
        print(f"✅ {service} | {masked} | {country}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

# ===================== API 1 FETCH (Token format) =====================
async def fetch_api1(last_ts):
    try:
        r = requests.get(
            API1_URL,
            params={"token": API1_TOKEN},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        if r.status_code != 200:
            return last_ts

        text = r.text.strip()
        if not text or not text.startswith('['):
            return last_ts

        data = r.json()
        if not isinstance(data, list) or len(data) == 0:
            return last_ts

        if last_ts is None:
            print(f"📌 API1 init: {data[0][3]}")
            return data[0][3]

        new_sms = [row for row in data if str(row[3]) > last_ts]
        if new_sms:
            print(f"📨 {len(new_sms)} new from API1")
            for row in reversed(new_sms):
                await send_sms(
                    str(row[0] or "Unknown"),
                    str(row[1] or ""),
                    str(row[2] or ""),
                    str(row[3] or "")
                )
            return data[0][3]

        return last_ts

    except Exception as e:
        print(f"❌ API1 error: {e}")
        return last_ts

# ===================== API 2 ZENEX FETCH =====================
# هذا هو التعديل: Zenex تعمل بشكل منفصل تماماً
async def fetch_zenex(last_ts):
    try:
        headers = {
            "mapikey": API2_TOKEN,
            "Accept": "application/json"
        }
        r = requests.get(API2_URL, headers=headers, timeout=10)
        if r.status_code != 200:
            return last_ts

        data = r.json()
        # Zenex data structure: {"data": {"otps": [...]}}
        otps = data.get("data", {}).get("otps", [])
        
        if not otps:
            return last_ts

        if last_ts is None:
            print(f"📌 Zenex init: {otps[0]['created_at']}")
            return otps[0]['created_at']

        new_sms = [i for i in otps if str(i["created_at"]) > last_ts]
        if new_sms:
            print(f"📨 {len(new_sms)} new from Zenex")
            for item in reversed(new_sms):
                await send_sms(
                    str(item.get("operator", "Zenex")),
                    str(item.get("number", "")),
                    str(item.get("otp", "")),
                    str(item.get("created_at", ""))
                )
            return otps[0]['created_at']

        return last_ts

    except Exception as e:
        print(f"❌ Zenex error: {e}")
        return last_ts

# ===================== API 3 FETCH (pscall format) =====================
async def fetch_api3(last_ts):
    try:
        r = requests.get(
            API3_URL,
            params={"key": API3_KEY, "start": 0, "length": 20},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
            verify=False
        )
        if r.status_code != 200:
            return last_ts

        data = r.json()
        if data.get("result") != "success":
            return last_ts

        items = data.get("data", [])
        if not items:
            return last_ts

        if last_ts is None:
            print(f"📌 API3 init: {items[0]['dateadded']}")
            return items[0]["dateadded"]

        new_sms = [i for i in items if str(i["dateadded"]) > last_ts]
        if new_sms:
            print(f"📨 {len(new_sms)} new from API3")
            for item in reversed(new_sms):
                await send_sms(
                    str(item.get("cli", "Unknown")),
                    str(item.get("num", "")),
                    str(item.get("sms", "")),
                    str(item.get("dateadded", ""))
                )
            return items[0]["dateadded"]

        return last_ts

    except Exception as e:
        print(f"❌ API3 error: {e}")
        return last_ts

# ===================== MAIN LOOP =====================
async def main_loop():
    print("🚀 Bot Started!")

    ts1 = None  # API1 timestamp
    ts2 = None  # Zenex timestamp
    ts3 = None  # API3 timestamp

    while True:
        ts1 = await fetch_api1(ts1)
        await asyncio.sleep(1)

        ts2 = await fetch_zenex(ts2)
        await asyncio.sleep(1)

        ts3 = await fetch_api3(ts3)

        await asyncio.sleep(5)

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    asyncio.run(main_loop())
