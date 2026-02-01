import telebot
import time
from threading import Thread
from flask import Flask
from datetime import datetime

TOKEN = '8528956901:AAErBMx_VE5QpsOo6Sv_APS26zWzVCeNwys'
bot = telebot.TeleBot(TOKEN)
ADMIN_PASSWORD = "4545"

# Базы данных
verified_admins = []
logs = []
user_styles = {} 
last_msg_time = {}
sent_messages = {} # Хранит ID сообщений для удаления {uid: [msg_ids]}

BAD_WORDS = ["мат1", "порно", "18+"]

app = Flask('')
@app.route('/')
def home(): return "EXTENDED_STYLES_ONLINE"

def run(): app.run(host="0.0.0.0", port=8080)

def check_safety(message):
    uid = message.from_user.id
    text = message.text.lower() if message.text else ""
    now = time.time()
    if uid in last_msg_time and now - last_msg_time[uid] < 0.7:
        bot.delete_message(message.chat.id, message.message_id)
        return False
    last_msg_time[uid] = now
    if any(word in text for word in BAD_WORDS):
        bot.delete_message(message.chat.id, message.message_id)
        return False
    return True

# --- РАСШИРЕННЫЕ СТИЛИ ---
def apply_style(text, style):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if style == "M O N O": return ' '.join(text.upper())
    if style == "Reverse": return text[::-1]
    if style == "Cyber": return f"⚡[01]{text.replace(' ','_')}[10]⚡"
    if style == "Gothic": return f"𝔊𝔬𝔱𝔥𝔦𝔠: {text}"
    if style == "Bubble": return f"Ⓤ {text} Ⓤ"
    if style == "SmallCaps": return text.lower().translate(str.maketrans(chars, "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"))
    if style == "Mirror": return f"| {text} | {text[::-1]}"
    if style == "Bold": return f"*{text}*"
    if style == "Underline": return f"_{text}_"
    if style == "Strike": return f"~{text}~"
    return text

@bot.message_handler(commands=['start'])
def start(message):
    if not check_safety(message): return
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎭 Стили текста", "🎬 Анимации")
    markup.add("🧹 Удалить мои сообщения", "🔙 Назад")
    bot.send_message(message.chat.id, "💻 **ТЕРМИНАЛ v.20.0**\nСтили и безопасность активны. Используй /delmy для очистки.", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🎭 Стили текста")
def style_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("M O N O", "Reverse", "Cyber", "Gothic", "Bubble")
    markup.add("SmallCaps", "Mirror", "Bold", "Underline", "Strike")
    markup.add("❌ Сбросить", "🔙 Назад")
    bot.send_message(message.chat.id, "Выберите стиль кодирования:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🎬 Анимации")
def anim_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📡 Передача", "💾 Загрузка", "🔙 Назад")
    bot.send_message(message.chat.id, "Выберите анимацию:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["M O N O","Reverse","Cyber","Gothic","Bubble","SmallCaps","Mirror","Bold","Underline","Strike","📡 Передача","💾 Загрузка"])
def set_style(message):
    user_styles[message.from_user.id] = message.text
    bot.send_message(message.chat.id, f"✅ Стиль {message.text} активирован.")

# --- КОМАНДА УДАЛЕНИЯ СВОИХ СООБЩЕНИЙ ---
@bot.message_handler(commands=['delmy'])
@bot.message_handler(func=lambda message: message.text == "🧹 Удалить мои сообщения")
def delete_my_messages(message):
    uid = message.from_user.id
    if uid in sent_messages and sent_messages[uid]:
        count = 0
        for m_id in sent_messages[uid]:
            try:
                bot.delete_message(message.chat.id, m_id)
                count += 1
            except: pass
        sent_messages[uid] = []
        bot.send_message(message.chat.id, f"✅ Удалено сообщений: {count}", delete_after=5)
    else:
        bot.send_message(message.chat.id, "❌ Ваши сообщения не найдены.")

# --- АДМИНКА (4545) ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin(message):
    verified_admins.append(message.from_user.id)
    bot.reply_to(message, "🔓 ТРОФИМ, ДОСТУП К ЛОГАМ ОТКРЫТ. (/logs)")

@bot.message_handler(commands=['logs'])
def show_logs(message):
    if message.from_user.id in verified_admins:
        bot.send_message(message.chat.id, "📡 ЛОГИ:\n" + "\n".join(logs[-10:]))

# --- ГЛАВНЫЙ ОБРАБОТЧИК ---
@bot.message_handler(func=lambda message: True)
def process_messages(message):
    if not check_safety(message): return
    uid = message.from_user.id
    name = message.from_user.first_name
    logs.append(f"[{datetime.now().strftime('%H:%M')}] {name}: {message.text}")

    if uid in user_styles:
        style = user_styles[uid]
        bot.delete_message(message.chat.id, message.message_id) # Стираем оригинал
        
        if style in ["📡 Передача", "💾 Загрузка"]:
            icon = "📡" if style == "📡 Передача" else "💾"
            m = bot.send_message(message.chat.id, f"{icon} {name}: Подключение...")
            # Сохраняем ID для удаления позже
            if uid not in sent_messages: sent_messages[uid] = []
            sent_messages[uid].append(m.message_id)
            
            for frame in [".", "..", "...", f"{message.text}"]:
                time.sleep(0.4)
                try: bot.edit_message_text(f"{icon} {name}: {frame}", message.chat.id, m.message_id)
                except: break
        else:
            final = apply_style(message.text, style)
            m = bot.send_message(message.chat.id, f"👤 {name}: {final}", parse_mode="Markdown" if style in ["Bold", "Underline", "Strike"] else None)
            if uid not in sent_messages: sent_messages[uid] = []
            sent_messages[uid].append(m.message_id)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
