import requests
import time
import json
import re
import random
import string
from datetime import datetime, timedelta
import os
import threading

# ================= CONFIG =================
BOT_TOKEN = "7991022648:AAFa7RhrVaaTMHktj2Nwjh10d5-al_K-Y6s"
NUMBER_API = "https://patel-number-api.vercel.app/number"
TG_API = "https://new-api-backup.vercel.app/?type=tg_num&key=swayam&query="
CAR_FULL_API = "https://vechile-info-cyan.vercel.app/api/vehicle/"
DEVELOPER = "𝗕𝗢𝗧 𝗗𝗘𝗩𝗘𝗟𝗢𝗣𝗘𝗥 @SOCIALBANNERR"
BOT_USERNAME = "Ind_numinfo_bot"
ADMIN_ID = 8647066036
LOADING_MSG = "⏳ ᴘʀᴏᴄᴇssɪɴɢ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ"
# ===========================================

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
OFFSET = 0
processed_updates = set()

# ============ DATA ============
user_data = {}
redeem_data = {}
ban_data = {}
unban_data = {}
redeem_codes = {}

def load_data():
    global user_data, redeem_data, ban_data, unban_data, redeem_codes
    try:
        with open("users.json", "r") as f:
            user_data = json.load(f)
    except:
        user_data = {}
    try:
        with open("redeem.json", "r") as f:
            redeem_data = json.load(f)
    except:
        redeem_data = {}
    try:
        with open("ban.json", "r") as f:
            ban_data = json.load(f)
    except:
        ban_data = {}
    try:
        with open("unban.json", "r") as f:
            unban_data = json.load(f)
    except:
        unban_data = {}
    try:
        with open("redeem_codes.json", "r") as f:
            redeem_codes = json.load(f)
    except:
        redeem_codes = {}

def save_data():
    try:
        with open("users.json", "w") as f:
            json.dump(user_data, f, indent=2)
    except:
        pass
    try:
        with open("redeem.json", "w") as f:
            json.dump(redeem_data, f, indent=2)
    except:
        pass
    try:
        with open("ban.json", "w") as f:
            json.dump(ban_data, f, indent=2)
    except:
        pass
    try:
        with open("unban.json", "w") as f:
            json.dump(unban_data, f, indent=2)
    except:
        pass
    try:
        with open("redeem_codes.json", "w") as f:
            json.dump(redeem_codes, f, indent=2)
    except:
        pass

def get_user(user_id):
    uid = str(user_id)
    if uid not in user_data:
        user_data[uid] = {"points": 10, "daily": None, "ref_by": None, "ref_count": 0, "first_name": "", "username": ""}
        save_data()
    return user_data[uid]

def update_points(user_id, points):
    uid = str(user_id)
    if uid not in user_data:
        user_data[uid] = {"points": 10, "daily": None, "ref_by": None, "ref_count": 0, "first_name": "", "username": ""}
    user_data[uid]["points"] = user_data[uid].get("points", 0) + points
    save_data()

def can_claim_daily(user_id):
    uid = str(user_id)
    if uid not in user_data:
        return True
    last = user_data[uid].get("daily")
    if not last:
        return True
    last_date = datetime.fromisoformat(last)
    return datetime.now() - last_date >= timedelta(hours=24)

def claim_daily(user_id):
    uid = str(user_id)
    user_data[uid]["daily"] = datetime.now().isoformat()
    save_data()

def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID)

def is_banned(user_id):
    return str(user_id) in ban_data

def generate_redeem_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# ============ SEND FILE ============
def send_file(chat_id, filename, data, reply_to=None):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        
        url = f"{BASE_URL}/sendDocument"
        files = {"document": open(filename, "rb")}
        payload = {"chat_id": chat_id}
        if reply_to:
            payload["reply_to_message_id"] = reply_to
        requests.post(url, data=payload, files=files, timeout=30)
        os.remove(filename)
        return True
    except Exception as e:
        print(f"❌ Send file error: {e}")
        return False

# ============ KEYBOARDS ============
def get_main_keyboard():
    return {
        "keyboard": [
            [{"text": "🖤 𝕾𝖊𝖆𝖗𝖈𝖍 🗡️"}],
            [{"text": "⚔️ 𝕽𝖊𝖋𝖊𝖗𝖗𝖊𝖊 🛡️"}, {"text": "💀 𝕯𝖆𝖎𝖑𝖞 🌑"}],
            [{"text": "🌙 𝕬𝖈𝖈𝖔𝖚𝖓𝖙 🌌"}, {"text": "🏴 𝕽𝖊𝖉𝖊𝖊𝖒 🔥"}],
            [{"text": "🌪️ 𝕳𝖊𝖑𝖕 🌊"}]
        ],
        "resize_keyboard": True,
        "is_persistent": True
    }

def get_search_keyboard():
    return {
        "keyboard": [
            [{"text": "📞 𝗡𝗨𝗠"}, {"text": "👤 𝗧𝗚"}],
            [{"text": "🆔 𝘾𝙃𝘼𝙏 𝙄𝘿"}, {"text": "🚘 𝗖𝗔𝗥 𝗙𝗨𝗟𝗟"}],  # 🔥 New Chat ID Button
            [{"text": "⬅️ ʙᴀᴄᴋ"}]
        ],
        "resize_keyboard": True,
        "is_persistent": True
    }

def get_cancel_keyboard():
    return {
        "keyboard": [
            [{"text": "❌ ᴄᴀɴᴄᴇʟ"}]
        ],
        "resize_keyboard": True,
        "is_persistent": True
    }

def get_admin_keyboard():
    return {
        "keyboard": [
            [{"text": "📊 sᴛᴀᴛs"}, {"text": "👥 ᴜsᴇʀs"}],
            [{"text": "📢 ʙʀᴏᴀᴅᴄᴀsᴛ"}, {"text": "🎯 ɢᴇɴ ʀᴇᴅᴇᴇᴍ"}],
            [{"text": "📂 ɢᴇᴛ ғɪʟᴇs"}, {"text": "🚫 ʙᴀɴ"}],
            [{"text": "✅ ᴜɴʙᴀɴ"}, {"text": "⬅️ ᴇxɪᴛ"}]
        ],
        "resize_keyboard": True,
        "is_persistent": True
    }

# ============ FORMATTERS ============
def format_number_anime(data, number):
    if not data.get("success"):
        return f"❌ ɴᴏ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ғᴏᴜɴᴅ\n\n⚡ {DEVELOPER}"
    records = data.get("records", [])
    if not records:
        return f"❌ ɴᴏ ʀᴇᴄᴏʀᴅs ғᴏᴜɴᴅ\n\n⚡ {DEVELOPER}"
    total = data.get('total_records', len(records))
    result = f"""📞 𝑵𝑼𝑴𝑩𝑬𝑹 𝑰𝑵𝑭𝑶
───────────────

🎯 𝑵𝒖𝒎𝒃𝒆𝒓: {number}
📚 𝑻𝒐𝒕𝒂𝒍: {total}
"""
    for i, rec in enumerate(records, 1):
        name = rec.get('NAME', 'ɴ/ᴀ')
        father = rec.get('fname', 'ɴ/ᴀ')
        aadhaar = rec.get('id', 'ɴ/ᴀ')
        alt = rec.get('alt', 'ɴ/ᴀ')
        carrier = rec.get('circle', 'ɴ/ᴀ')
        address = rec.get('ADDRESS', 'ɴ/ᴀ')
        result += f"""
𝑹𝒆𝒄𝒐𝒓𝒅 #{i}
───────────────
👤 𝑵𝒂𝒎𝒆: {name}
👨 𝑭𝒂𝒕𝒉𝒆𝒓: {father}
🆔 𝑨𝒂𝒅𝒉𝒂𝒂𝒓: {aadhaar}
📞 𝑨𝒍𝒕𝒆𝒓𝒏𝒂𝒕𝒆: {alt}
📡 𝑪𝒂𝒓𝒓𝒊𝒆𝒓: {carrier}
📍 𝑨𝒅𝒅𝒓𝒆𝒔𝒔: {address}
"""
    result += f"""
───────────────
⚡ {DEVELOPER}"""
    return result

def format_tg_anime(data, query):
    """Format Telegram info - For TG button"""
    
    if not data.get("status") == "success":
        error_msg = data.get("error", "No information found")
        return f"""❌ ɴᴏ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ғᴏᴜɴᴅ
───────────────
📝 {error_msg}

⚡ {DEVELOPER}"""
    
    results = data.get("results", {})
    number = results.get('number', 'ɴ/ᴀ')
    country = results.get('country', 'ɴ/ᴀ')
    country_code = results.get('country_code', 'ɴ/ᴀ')
    cached = results.get('cached', False)
    
    username = query if query.startswith('@') else f'@{query}'
    tg_id = query if query.isdigit() else 'ɴ/ᴀ'
    
    response = f"""👤 𝑻𝑮 𝑰𝑵𝑭𝑶
───────────────

👤 𝑼𝒔𝒆𝒓𝒏𝒂𝒎𝒆: {username}"""
    
    if tg_id != 'ɴ/ᴀ':
        response += f"\n🆔 𝑻𝑮 𝑰𝑫: {tg_id}"
    
    if number != 'ɴ/ᴀ':
        response += f"\n📞 𝑵𝒖𝒎𝒃𝒆𝒓: {number}"
    
    if country != 'ɴ/ᴀ':
        response += f"\n🌍 𝑪𝒐𝒖𝒏𝒕𝒓𝒚: {country} ({country_code})"
    
    response += f"""
💾 𝑪𝒂𝒄𝒉𝒆𝒅: {'✅ Yes' if cached else '❌ No'}

───────────────
⚡ {DEVELOPER}"""
    
    return response

def format_chat_id_anime(data, query):
    """🔥 Format Chat ID to Number - Clean output"""
    
    if not data.get("status") == "success":
        error_msg = data.get("error", "No information found")
        return f"""❌ ɴᴏ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ғᴏᴜɴᴅ
───────────────
📝 {error_msg}

⚡ {DEVELOPER}"""
    
    results = data.get("results", {})
    number = results.get('number', 'ɴ/ᴀ')
    country = results.get('country', 'ɴ/ᴀ')
    country_code = results.get('country_code', 'ɴ/ᴀ')
    cached = results.get('cached', False)
    tg_id = query if query.isdigit() else 'ɴ/ᴀ'
    
    response = f"""👤 𝑻𝑮 𝘾𝙃𝘼𝙏 𝙄𝘿
───────────────

🆔 𝑻𝑮 𝑰𝑫: {tg_id}"""
    
    if number != 'ɴ/ᴀ':
        response += f"\n📞 𝑵𝒖𝒎𝒃𝒆𝒓: {number}"
    
    if country != 'ɴ/ᴀ':
        response += f"\n🌍 𝑪𝒐𝒖𝒏𝒕𝒓𝒚: {country} ({country_code})"
    
    response += f"""
💾 𝑪𝒂𝒄𝒉𝒆𝒅: {'✅ Yes' if cached else '❌ No'}

───────────────
⚡ {DEVELOPER}"""
    
    return response

def format_car_full(data, vehicle):
    if not data.get("result"):
        return f"❌ ɴᴏ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ғᴏᴜɴᴅ\n\n⚡ {DEVELOPER}"
    
    result = data.get("result", {})
    vehicle_data = result.get("vehicle_data", {})
    
    if not vehicle_data:
        return f"❌ ɴᴏ ᴠᴇʜɪᴄʟᴇ ᴅᴀᴛᴀ ғᴏᴜɴᴅ\n\n⚡ {DEVELOPER}"
    
    reg_no = vehicle_data.get('regNo', 'ɴ/ᴀ')
    owner = vehicle_data.get('owner', 'ɴ/ᴀ')
    owner_father = vehicle_data.get('ownerFatherName', 'ɴ/ᴀ')
    vehicle_name = vehicle_data.get('vehicle', 'ɴ/ᴀ')
    manufacturer = vehicle_data.get('manufacturer', 'ɴ/ᴀ')
    manufacturer_year = vehicle_data.get('manufacturerYear', 'ɴ/ᴀ')
    reg_date = vehicle_data.get('regDate', 'ɴ/ᴀ')
    reg_authority = vehicle_data.get('regAuthority', 'ɴ/ᴀ')
    fuel_type = vehicle_data.get('fuelType', 'ɴ/ᴀ')
    vehicle_class = vehicle_data.get('vehicleClass', 'ɴ/ᴀ')
    vehicle_type = vehicle_data.get('vehicleType', 'ɴ/ᴀ')
    chassis = vehicle_data.get('chassis', 'ɴ/ᴀ')
    engine = vehicle_data.get('engine', 'ɴ/ᴀ')
    insurance_company = vehicle_data.get('insuranceCompanyName', 'ɴ/ᴀ')
    insurance_policy = vehicle_data.get('insurancePolicyNumber', 'ɴ/ᴀ')
    insurance_upto = vehicle_data.get('insuranceUpto', 'ɴ/ᴀ')
    insurance_expired = vehicle_data.get('insuranceExpired', False)
    pucc_number = vehicle_data.get('puccNumber', 'ɴ/ᴀ')
    pucc_valid = vehicle_data.get('puccValidUpto', 'ɴ/ᴀ')
    financer = vehicle_data.get('financerName', 'ɴ/ᴀ')
    status = vehicle_data.get('status', 'ɴ/ᴀ')
    mobile = result.get('mobile_number', 'ɴ/ᴀ')
    
    insurance_status = "✅ ᴀᴄᴛɪᴠᴇ" if not insurance_expired else "❌ ᴇxᴘɪʀᴇᴅ"
    
    return f"""🚗 𝑪𝑨𝑹 𝑭𝑼𝑳𝑳 𝑫𝑬𝑻𝑨𝑰𝑳𝑺
───────────────

📌 <b>ʀᴇɢɪsᴛʀᴀᴛɪᴏɴ</b>
🎯 ɴᴜᴍʙᴇʀ: {reg_no}
📅 ᴅᴀᴛᴇ: {reg_date}
🏛️ ᴀᴜᴛʜᴏʀɪᴛʏ: {reg_authority}

👤 <b>ᴏᴡɴᴇʀ</b>
ɴᴀᴍᴇ: {owner}
ғᴀᴛʜᴇʀ: {owner_father}
📞 ᴍᴏʙɪʟᴇ: {mobile}

🚘 <b>ᴠᴇʜɪᴄʟᴇ</b>
ɴᴀᴍᴇ: {vehicle_name}
🏭 ᴍᴀɴᴜғᴀᴄᴛᴜʀᴇʀ: {manufacturer}
📅 ʏᴇᴀʀ: {manufacturer_year}
⛽ ғᴜᴇʟ: {fuel_type}
🚦 ᴄʟᴀss: {vehicle_class}
📦 ᴛʏᴘᴇ: {vehicle_type}
🔢 ᴄʜᴀssɪs: {chassis}
🔧 ᴇɴɢɪɴᴇ: {engine}

🏥 <b>ɪɴsᴜʀᴀɴᴄᴇ</b>
📋 ᴄᴏᴍᴘᴀɴʏ: {insurance_company}
📄 ᴘᴏʟɪᴄʏ: {insurance_policy}
📅 ᴜᴘᴛᴏ: {insurance_upto}
📊 sᴛᴀᴛᴜs: {insurance_status}

📄 <b>ᴘᴜᴄᴄ</b>
ɴᴜᴍʙᴇʀ: {pucc_number}
ᴠᴀʟɪᴅ ᴜᴘᴛᴏ: {pucc_valid}

💰 <b>ғɪɴᴀɴᴄɪᴀʟ</b>
ғɪɴᴀɴᴄᴇʀ: {financer}
sᴛᴀᴛᴜs: {status}

───────────────
⚡ {DEVELOPER}"""

# ============ WELCOME ============
def get_welcome(first_name, user_id):
    user = get_user(user_id)
    points = user.get("points", 0)
    return f"""🖤 𝗛𝗲𝗹𝗹𝗼, {first_name} 🗡️
───────────────
🌙 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 𝗜𝗻𝗳𝗼 𝗕𝗼𝘁 🌑

🌟 𝗣𝗼𝗶𝗻𝘁𝘀: {points}

⚔️ 𝗖𝗵𝗼𝗼𝘀𝗲 𝗮𝗻 𝗼𝗽𝘁𝗶𝗼𝗻 🛡️

───────────────
⚡ {DEVELOPER}"""

def get_search_menu():
    return f"""🖤 𝗦𝗘𝗔𝗥𝗖𝗛 🗡️
───────────────

📞 𝗡𝘂𝗺𝗯𝗲𝗿 → 10-ᴅɪɢɪᴛ
👤 𝗧𝗚 → @ᴜsᴇʀɴᴀᴍᴇ
🆔 𝘾𝙃𝘼𝙏 𝙄𝘿 → ɪᴅ
🚘 𝗖𝗔𝗥 𝗙𝗨𝗟𝗟 → ᴠᴇʜɪᴄʟᴇ ɴᴏ

───────────────
⚡ {DEVELOPER}"""

# ============ API CALLS ============
def get_number_info(number):
    try:
        url = f"{NUMBER_API}?number={number}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return {"success": False}
    except:
        return {"success": False}

def get_tg_info(query):
    try:
        query = query.strip()
        if query.startswith("@"):
            query = query[1:]
        
        url = f"{TG_API}{query}"
        resp = requests.get(url, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success":
                return data
            return {"status": "failed", "error": data.get("error", "No data found")}
        return {"status": "failed"}
    except:
        return {"status": "failed"}

def get_car_full_info(vehicle):
    try:
        url = f"{CAR_FULL_API}{vehicle}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return {"result": None}
    except:
        return {"result": None}

# ============ SEND MESSAGE ============
def send_msg(chat_id, text, reply_to=None, parse_mode="HTML", reply_markup=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "allow_sending_without_reply": True
    }
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        requests.post(url, json=payload, timeout=15)
    except:
        pass

# ============ VALIDATORS ============
def is_valid_number(text):
    return text.isdigit() and len(text) == 10

def is_valid_username(text):
    text = text.strip()
    if text.startswith("@"):
        text = text[1:]
    return len(text) >= 3 and re.match(r'^[a-zA-Z0-9_]+$', text) is not None

def is_valid_id(text):
    return text.isdigit() and len(text) >= 5

def is_valid_vehicle(text):
    text = text.upper().strip()
    return re.match(r'^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$', text) is not None

# ============ ADMIN PANEL ============
def send_admin_panel(chat_id):
    text = f"""👑 𝗔𝗱𝗺𝗶𝗻 𝗣𝗮𝗻𝗲𝗹
───────────────

📊 𝗦𝘁𝗮𝘁𝘀
👥 Users: {len(user_data)}
💳 Redeems: {len(redeem_data)}
🚫 Banned: {len(ban_data)}
✅ Unban: {len(unban_data)}
🎯 Codes: {len(redeem_codes)}

───────────────
⚡ {DEVELOPER}"""
    send_msg(chat_id, text, reply_markup=get_admin_keyboard(), parse_mode="HTML")

# ============ WEB SERVER ============
try:
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "🤖 Bot is running!"
    
    def run_web():
        app.run(host='0.0.0.0', port=8080)
    
    threading.Thread(target=run_web, daemon=True).start()
    print("🌐 Web server started")
except:
    pass

# ============ MAIN LOOP ============
def main():
    global OFFSET, processed_updates
    load_data()
    print("🖤 GOTHIC BOT STARTED 🗡️")
    print(f"⚡ {DEVELOPER}")
    print("=" * 40)

    admin_mode = False
    broadcast_mode = False
    ban_mode = False
    unban_mode = False
    gen_redeem_mode = False
    last_search_type = {}

    while True:
        try:
            resp = requests.get(f"{BASE_URL}/getUpdates", params={"offset": OFFSET, "timeout": 10}, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok"):
                    for update in data.get("result", []):
                        update_id = update.get("update_id")
                        
                        if update_id in processed_updates:
                            continue
                        processed_updates.add(update_id)
                        OFFSET = update_id + 1

                        if "callback_query" in update:
                            callback = update["callback_query"]
                            chat_id = callback["message"]["chat"]["id"]
                            data = callback["data"]
                            if data == "cancel":
                                send_msg(chat_id, "❌ ᴄᴀɴᴄᴇʟʟᴇᴅ", reply_markup=get_main_keyboard())
                            continue

                        msg = update.get("message")
                        if not msg:
                            continue

                        chat_id = msg.get("chat", {}).get("id")
                        text = msg.get("text", "")
                        message_id = msg.get("message_id")
                        user_id = msg.get("from", {}).get("id")
                        first_name = msg.get("from", {}).get("first_name", "User")
                        username = msg.get("from", {}).get("username", "")

                        uid = str(user_id)
                        if uid in user_data:
                            user_data[uid]["first_name"] = first_name
                            user_data[uid]["username"] = username
                            save_data()

                        if is_banned(user_id) and not is_admin(user_id):
                            send_msg(chat_id, "🚫 ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ.", reply_to=message_id)
                            continue

                        # ===== START =====
                        if text and text.startswith("/start"):
                            ref_match = re.search(r'ref_(\d+)', text)
                            if ref_match:
                                ref_by = ref_match.group(1)
                                if str(user_id) != ref_by and not is_banned(ref_by):
                                    update_points(ref_by, 10)
                                    uid = str(user_id)
                                    if uid not in user_data:
                                        user_data[uid] = {"points": 10, "daily": None, "ref_by": ref_by, "ref_count": 0, "first_name": first_name, "username": username}
                                    else:
                                        user_data[uid]["ref_by"] = ref_by
                                    if ref_by in user_data:
                                        user_data[ref_by]["ref_count"] = user_data[ref_by].get("ref_count", 0) + 1
                                    save_data()
                                    send_msg(chat_id, f"🎉 ʀᴇғᴇʀʀᴇᴅ ʙʏ {ref_by}\n\n✨ ʏᴏᴜ ɢᴏᴛ 10 ᴘᴏɪɴᴛs!", parse_mode="HTML")
                            
                            welcome = get_welcome(first_name, user_id)
                            send_msg(chat_id, welcome, reply_markup=get_main_keyboard(), parse_mode="HTML")
                            continue

                        # ===== REDEEM CODE =====
                        if text and len(text) == 8 and text.isalnum() and text.upper() == text:
                            code = text.upper()
                            if code in redeem_codes and redeem_codes[code].get("used") == False:
                                points = redeem_codes[code].get("points", 0)
                                update_points(user_id, points)
                                redeem_codes[code]["used"] = True
                                redeem_codes[code]["used_by"] = str(user_id)
                                save_data()
                                send_msg(chat_id, f"🎉 <b>ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ ᴜsᴇᴅ!</b>\n\n➕ {points} ᴘᴏɪɴᴛs ᴀᴅᴅᴇᴅ\n\n🌟 ᴘᴏɪɴᴛs: {get_user(user_id).get('points', 0)}", reply_to=message_id, parse_mode="HTML")
                                continue
                            elif code in redeem_codes and redeem_codes[code].get("used") == True:
                                send_msg(chat_id, "❌ ᴛʜɪs ᴄᴏᴅᴇ ʜᴀs ᴀʟʀᴇᴀᴅʏ ʙᴇᴇɴ ᴜsᴇᴅ!", reply_to=message_id)
                                continue
                            else:
                                send_msg(chat_id, "❌ ɪɴᴠᴀʟɪᴅ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ!", reply_to=message_id)
                                continue

                        # ===== ADMIN =====
                        if text == "/admin":
                            if is_admin(user_id):
                                admin_mode = True
                                send_admin_panel(chat_id)
                            else:
                                send_msg(chat_id, "❌ ᴜɴᴀᴜᴛʜᴏʀɪsᴇᴅ ᴀᴄᴄᴇss!", reply_to=message_id)
                            continue

                        if admin_mode and is_admin(user_id):
                            if text == "⬅️ ᴇxɪᴛ":
                                admin_mode = False
                                send_msg(chat_id, "👋 ᴇxɪᴛɪɴɢ ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", reply_markup=get_main_keyboard())
                                continue
                            elif text == "📊 sᴛᴀᴛs":
                                send_admin_panel(chat_id)
                                continue
                            elif text == "👥 ᴜsᴇʀs":
                                if user_data:
                                    msg_text = "👥 <b>ᴜsᴇʀ ʟɪsᴛ</b>\n\n"
                                    for uid, data in list(user_data.items()):
                                        pts = data.get("points", 0)
                                        ref = data.get("ref_count", 0)
                                        name = data.get("first_name", "Unknown")
                                        uname = data.get("username", "")
                                        msg_text += f"🆔 {uid}\n   👤 {name} (@{uname})\n   ⭐ {pts} pts | 👥 {ref} refs\n\n"
                                    send_msg(chat_id, msg_text, parse_mode="HTML")
                                else:
                                    send_msg(chat_id, "❌ ɴᴏ ᴜsᴇʀs ғᴏᴜɴᴅ")
                                continue
                            elif text == "📢 ʙʀᴏᴀᴅᴄᴀsᴛ":
                                broadcast_mode = True
                                send_msg(chat_id, "📢 sᴇɴᴅ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ (ᴛʏᴘᴇ /ᴄᴀɴᴄᴇʟ)")
                                continue
                            elif text == "🎯 ɢᴇɴ ʀᴇᴅᴇᴇᴍ":
                                gen_redeem_mode = True
                                send_msg(chat_id, "🎯 sᴇɴᴅ ᴘᴏɪɴᴛs ᴀᴍᴏᴜɴᴛ ғᴏʀ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ\nᴇxᴀᴍᴘʟᴇ: 50")
                                continue
                            elif text == "📂 ɢᴇᴛ ғɪʟᴇs":
                                files = {
                                    "users.json": user_data,
                                    "redeem.json": redeem_data,
                                    "ban.json": ban_data,
                                    "unban.json": unban_data,
                                    "redeem_codes.json": redeem_codes
                                }
                                for filename, file_data in files.items():
                                    try:
                                        send_file(chat_id, filename, file_data, reply_to=message_id)
                                        time.sleep(0.5)
                                    except Exception as e:
                                        send_msg(chat_id, f"❌ ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ {filename}: {e}", reply_to=message_id)
                                continue
                            elif text == "🚫 ʙᴀɴ":
                                ban_mode = True
                                send_msg(chat_id, "🚫 sᴇɴᴅ ᴜsᴇʀ ɪᴅ ᴛᴏ ʙᴀɴ\nᴇxᴀᴍᴘʟᴇ: 123456789")
                                continue
                            elif text == "✅ ᴜɴʙᴀɴ":
                                unban_mode = True
                                send_msg(chat_id, "✅ sᴇɴᴅ ᴜsᴇʀ ɪᴅ ᴛᴏ ᴜɴʙᴀɴ\nᴇxᴀᴍᴘʟᴇ: 123456789")
                                continue

                        # ===== GENERATE REDEEM =====
                        if gen_redeem_mode and is_admin(user_id):
                            if text.isdigit() and int(text) > 0:
                                points = int(text)
                                code = generate_redeem_code()
                                redeem_codes[code] = {"points": points, "used": False, "used_by": None, "created": datetime.now().isoformat()}
                                save_data()
                                send_msg(chat_id, f"🎯 <b>ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ ɢᴇɴᴇʀᴀᴛᴇᴅ!</b>\n\n📝 <code>{code}</code>\n💰 {points} ᴘᴏɪɴᴛs\n\nsᴇɴᴅ ᴛʜɪs ᴄᴏᴅᴇ ᴛᴏ ᴜsᴇʀ", parse_mode="HTML")
                                gen_redeem_mode = False
                            elif text == "/cancel":
                                gen_redeem_mode = False
                                send_msg(chat_id, "❌ ɢᴇɴᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ", reply_markup=get_admin_keyboard())
                            continue

                        # ===== BROADCAST =====
                        if broadcast_mode and is_admin(user_id):
                            if text == "/cancel":
                                broadcast_mode = False
                                send_msg(chat_id, "❌ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ", reply_markup=get_admin_keyboard())
                                continue
                            elif text and text != "📢 ʙʀᴏᴀᴅᴄᴀsᴛ":
                                sent = 0
                                for uid in user_data:
                                    try:
                                        send_msg(int(uid), f"📢 <b>ʙʀᴏᴀᴅᴄᴀsᴛ</b>\n\n{text}")
                                        sent += 1
                                        time.sleep(0.05)
                                    except:
                                        pass
                                send_msg(chat_id, f"✅ sᴇɴᴛ ᴛᴏ {sent}/{len(user_data)} ᴜsᴇʀs")
                                broadcast_mode = False
                                send_admin_panel(chat_id)
                                continue

                        # ===== BAN =====
                        if ban_mode and is_admin(user_id):
                            if text.isdigit():
                                ban_data[text] = True
                                save_data()
                                send_msg(chat_id, f"✅ ᴜsᴇʀ {text} ʙᴀɴɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!")
                                ban_mode = False
                                send_admin_panel(chat_id)
                            elif text == "/cancel":
                                ban_mode = False
                                send_msg(chat_id, "❌ ʙᴀɴ ᴄᴀɴᴄᴇʟʟᴇᴅ", reply_markup=get_admin_keyboard())
                            continue

                        # ===== UNBAN =====
                        if unban_mode and is_admin(user_id):
                            if text.isdigit():
                                if text in ban_data:
                                    del ban_data[text]
                                    unban_data[text] = True
                                    save_data()
                                    send_msg(chat_id, f"✅ ᴜsᴇʀ {text} ᴜɴʙᴀɴɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!")
                                else:
                                    send_msg(chat_id, f"❌ ᴜsᴇʀ {text} ɴᴏᴛ ʙᴀɴɴᴇᴅ")
                                unban_mode = False
                                send_admin_panel(chat_id)
                            elif text == "/cancel":
                                unban_mode = False
                                send_msg(chat_id, "❌ ᴜɴʙᴀɴ ᴄᴀɴᴄᴇʟʟᴇᴅ", reply_markup=get_admin_keyboard())
                            continue

                        # ===== MAIN MENU BUTTONS =====
                        if text == "🖤 𝕾𝖊𝖆𝖗𝖈𝖍 🗡️":
                            send_msg(chat_id, get_search_menu(), reply_markup=get_search_keyboard(), parse_mode="HTML")
                            continue

                        if text == "⬅️ ʙᴀᴄᴋ":
                            welcome = get_welcome(first_name, user_id)
                            send_msg(chat_id, welcome, reply_markup=get_main_keyboard(), parse_mode="HTML")
                            continue

                        if text == "❌ ᴄᴀɴᴄᴇʟ":
                            send_msg(chat_id, get_search_menu(), reply_markup=get_search_keyboard(), parse_mode="HTML")
                            continue

                        if text == "⚔️ 𝕽𝖊𝖋𝖊𝖗𝖗𝖊𝖊 🛡️":
                            ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
                            points = get_user(user_id).get("points", 0)
                            ref_count = get_user(user_id).get("ref_count", 0)
                            send_msg(chat_id,
                                f"""⚔️ 𝗥𝗘𝗙𝗘𝗥𝗥𝗔𝗟 🛡️
───────────────

🔗 <code>{ref_link}</code>

👥 ᴛᴏᴛᴀʟ ʀᴇғs: {ref_count}
🌟 ᴘᴏɪɴᴛs: {points}

✨ ʀᴇғᴇʀ = 10 ᴘᴏɪɴᴛs
✨ ᴅᴀɪʟʏ = 10 ᴘᴏɪɴᴛs

───────────────
⚡ {DEVELOPER}""",
                                reply_to=message_id, parse_mode="HTML")
                            continue

                        if text == "💀 𝕯𝖆𝖎𝖑𝖞 🌑":
                            if can_claim_daily(user_id):
                                update_points(user_id, 10)
                                claim_daily(user_id)
                                points = get_user(user_id).get("points", 0)
                                send_msg(chat_id,
                                    f"""💀 𝗗𝗔𝗜𝗟𝗬 𝗖𝗟𝗔𝗜𝗠𝗘𝗗! 🌑
───────────────

➕ 10 ᴘᴏɪɴᴛs ᴀᴅᴅᴇᴅ

🌟 𝗣𝗼𝗶𝗻𝘁𝘀: {points}

───────────────
⚡ {DEVELOPER}""",
                                    reply_to=message_id, parse_mode="HTML")
                            else:
                                send_msg(chat_id,
                                    f"""⏳ 𝗔𝗟𝗥𝗘𝗔𝗗𝗬 𝗖𝗟𝗔𝗜𝗠𝗘𝗗!
───────────────

ᴄᴏᴍᴇ ʙᴀᴄᴋ ᴀғᴛᴇʀ 24 ʜᴏᴜʀs

───────────────
⚡ {DEVELOPER}""",
                                    reply_to=message_id, parse_mode="HTML")
                            continue

                        if text == "🌙 𝕬𝖈𝖈𝖔𝖚𝖓𝖙 🌌":
                            user = get_user(user_id)
                            points = user.get("points", 0)
                            ref_count = user.get("ref_count", 0)
                            ref_by = user.get("ref_by", "ɴᴏɴᴇ")
                            send_msg(chat_id,
                                f"""🌙 𝗔𝗖𝗖𝗢𝗨𝗡𝗧 🌌
───────────────

🌟 ᴘᴏɪɴᴛs: {points}
👥 ʀᴇғᴇʀʀᴀʟs: {ref_count}
🔗 ʀᴇғғᴇʀʀᴇᴅ ʙʏ: {ref_by}

───────────────
⚡ {DEVELOPER}""",
                                reply_to=message_id, parse_mode="HTML")
                            continue

                        if text == "🏴 𝕽𝖊𝖉𝖊𝖊𝖒 🔥":
                            send_msg(chat_id,
                                f"""🏴 𝗥𝗘𝗗𝗘𝗘𝗠 🔥
───────────────

ᴇɴᴛᴇʀ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ (8 ᴄʜᴀʀᴀᴄᴛᴇʀs)
ᴇxᴀᴍᴘʟᴇ: ABCD1234

───────────────
⚡ {DEVELOPER}""",
                                reply_to=message_id, parse_mode="HTML")
                            continue

                        if text == "🌪️ 𝕳𝖊𝖑𝖕 🌊":
                            send_msg(chat_id,
                                f"""🌪️ 𝗛𝗘𝗟𝗣 🌊
───────────────

🖤 sᴇᴀʀᴄʜ 🗡️ → ɴᴜᴍʙᴇʀ/ᴛɢ/ᴄᴀʀ
💀 ᴅᴀɪʟʏ 🌑 → +10 ᴘᴏɪɴᴛs (24ʜ)
⚔️ ʀᴇғᴇʀʀᴇᴇ 🛡️ → ɪɴᴠɪᴛᴇ ғʀɪᴇɴᴅs
🌙 ᴀᴄᴄᴏᴜɴᴛ 🌌 → ᴄʜᴇᴄᴋ ᴘᴏɪɴᴛs
🏴 ʀᴇᴅᴇᴇᴍ 🔥 → ᴇɴᴛᴇʀ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ

⚡ 1 sᴇᴀʀᴄʜ = -1 ᴘᴏɪɴᴛ

───────────────
⚡ {DEVELOPER}""",
                                reply_to=message_id, parse_mode="HTML")
                            continue

                        # ===== SEARCH BUTTONS =====
                        if text == "📞 𝗡𝗨𝗠":
                            send_msg(chat_id,
                                f"""📞 𝗡𝗨𝗠𝗕𝗘𝗥
───────────────

sᴇɴᴅ 10-ᴅɪɢɪᴛ ɴᴜᴍʙᴇʀ
ᴇxᴀᴍᴘʟᴇ: 9693615642

───────────────
⚡ {DEVELOPER}""",
                                reply_markup=get_cancel_keyboard(), parse_mode="HTML")
                            last_search_type[str(user_id)] = "number"
                            continue

                        if text == "👤 𝗧𝗚":
                            send_msg(chat_id,
                                f"""👤 𝗧𝗚
───────────────

sᴇɴᴅ @ᴜsᴇʀɴᴀᴍᴇ
ᴇxᴀᴍᴘʟᴇ: @SOCIALBANNERR

───────────────
⚡ {DEVELOPER}""",
                                reply_markup=get_cancel_keyboard(), parse_mode="HTML")
                            last_search_type[str(user_id)] = "tg"
                            continue

                        # 🔥 NEW CHAT ID BUTTON
                        if text == "🆔 𝘾𝙃𝘼𝙏 𝙄𝘿":
                            send_msg(chat_id,
                                f"""🆔 𝘾𝙃𝘼𝙏 𝙄𝘿
───────────────

sᴇɴᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴜsᴇʀ ɪᴅ
ᴇxᴀᴍᴘʟᴇ: 6323367629

───────────────
⚡ {DEVELOPER}""",
                                reply_markup=get_cancel_keyboard(), parse_mode="HTML")
                            last_search_type[str(user_id)] = "chat_id"
                            continue

                        if text == "🚘 𝗖𝗔𝗥 𝗙𝗨𝗟𝗟":
                            send_msg(chat_id,
                                f"""🚘 𝗖𝗔𝗥 𝗙𝗨𝗟𝗟
───────────────

sᴇɴᴅ ᴠᴇʜɪᴄʟᴇ ɴᴜᴍʙᴇʀ
ᴇxᴀᴍᴘʟᴇ: MH02FY8945

───────────────
⚡ {DEVELOPER}""",
                                reply_markup=get_cancel_keyboard(), parse_mode="HTML")
                            last_search_type[str(user_id)] = "car_full"
                            continue

                        # ===== DIRECT INPUTS =====
                        if is_valid_number(text):
                            update_points(user_id, -1)
                            send_msg(chat_id, LOADING_MSG, reply_to=message_id, parse_mode="HTML")
                            result = get_number_info(text)
                            formatted = format_number_anime(result, text)
                            blockquote = f"<blockquote expandable>\n{formatted}\n</blockquote>"
                            send_msg(chat_id, blockquote, reply_to=message_id, parse_mode="HTML", reply_markup=get_cancel_keyboard())
                            continue

                        if is_valid_vehicle(text):
                            vehicle = text.upper()
                            send_msg(chat_id, LOADING_MSG, reply_to=message_id, parse_mode="HTML")
                            result = get_car_full_info(vehicle)
                            if result.get("result"):
                                formatted = format_car_full(result, vehicle)
                                blockquote = f"<blockquote expandable>\n{formatted}\n</blockquote>"
                                send_msg(chat_id, blockquote, reply_to=message_id, parse_mode="HTML", reply_markup=get_cancel_keyboard())
                            else:
                                send_msg(chat_id, "❌ ɴᴏ ғᴜʟʟ ᴅᴇᴛᴀɪʟs ғᴏᴜɴᴅ\n\nᴛʀʏ /ᴄᴀɴᴄᴇʟ", reply_to=message_id)
                            continue

                        # ===== TG USERNAME =====
                        if is_valid_username(text):
                            update_points(user_id, -1)
                            username = text if text.startswith("@") else "@" + text
                            send_msg(chat_id, LOADING_MSG, reply_to=message_id, parse_mode="HTML")
                            result = get_tg_info(username)
                            formatted = format_tg_anime(result, username)
                            blockquote = f"<blockquote expandable>\n{formatted}\n</blockquote>"
                            send_msg(chat_id, blockquote, reply_to=message_id, parse_mode="HTML", reply_markup=get_cancel_keyboard())
                            continue

                        # 🔥 NEW CHAT ID INPUT
                        if is_valid_id(text):
                            search_type = last_search_type.get(str(user_id), "")
                            
                            # Only if user clicked CHAT ID button
                            if search_type == "chat_id":
                                update_points(user_id, -1)
                                send_msg(chat_id, LOADING_MSG, reply_to=message_id, parse_mode="HTML")
                                result = get_tg_info(text)
                                formatted = format_chat_id_anime(result, text)
                                blockquote = f"<blockquote expandable>\n{formatted}\n</blockquote>"
                                send_msg(chat_id, blockquote, reply_to=message_id, parse_mode="HTML", reply_markup=get_cancel_keyboard())
                                continue
                            else:
                                # Agar kisi aur button se ID aayi toh ignore karo
                                pass

            time.sleep(0.1)
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
