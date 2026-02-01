import telebot
import time
import random
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
sent_messages = {}

BAD_WORDS = ["мат1", "порно", "18+", "хентай"]

app = Flask('')
@app.route('/')
def home(): return "SECURE_SYSTEM_V23"

def run(): app.run(host="0.0.0.0", port=8080)

# --- МОДУЛЬ БЕЗОПАСНОСТИ ---
def check_safety(message):
    uid = message.from_user.id
    text = message.text.lower() if message.text else ""
    now = time.time()
    if uid in last_msg_time and now - last_msg_time[uid] < 0.6:
        bot.delete_message(message.chat.id, message.message_id)
        return False
    last_msg_time[uid] = now
    if any(word in text for word in BAD_WORDS):
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "⚠️ Система: Обнаружена угроза безопасности. Сообщение стерто.")
        return False
    return True

# --- СТИЛИ ТЕКСТА ---
def apply_style(text, style):
    if style == "M O N O": return ' '.join(text.upper())
    if style == "Reverse": return text[::-1]
    if style == "Cyber": return f"⚡[01]{text.replace(' ','_')}[10]⚡"
    if style == "Gothic": return f"𝔊𝔬𝔱𝔥𝔦𝔠: {text}"
    if style == "Bubble": return f"Ⓤ {text} Ⓤ"
    if style == "SmallCaps": return text.lower().translate(str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"))
    if style == "Mirror": return f"{text} | {text[::-1]}"
    if style == "Bold": return f"*{text}*"
    if style == "Underline": return f"_{text}_"
    if style == "Strike": return f"~{text}~"
    return text

# --- МЕНЮ ---
@bot.message_handler(commands=['start'])
def start(message):
    if not check_safety(message): return
    main_menu(message)

def main_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎭 Стили текста", "🎬 Анимации")
    markup.add("🛡 Безопасность", "🧹 Удалить мои сообщения")
    markup.add("❌ Сбросить всё")
    bot.send_message(message.chat.id, "💻 **СИСТЕМА УПРАВЛЕНИЯ v.23.0**\nВыберите модуль:", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🛡 Безопасность")
def security_status(message):
    status = (
        "🛡 **ОТЧЕТ БЕЗОПАСНОСТИ**\n"
        "--------------------------\n"
        "✅ Анти-спам: АКТИВЕН\n"
        "✅ Фильтр матов: АКТИВЕН\n"
        "✅ Защита 18+: АКТИВНА\n"
        "✅ Логирование: ВЕДЕТСЯ\n"
        "--------------------------"
    )
    bot.send_message(message.chat.id, status, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🎬 Анимации")
def anim_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📡 Передача", "💾 Загрузка", "⌨️ Печать")
    markup.add("🔍 Сканирование", "🔓 Взлом")
    markup.add("🔙 Назад")
    bot.send_message(message.chat.id, "Выберите режим анимации:", reply_markup=markup)

# --- АДМИНКА ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin_login(message):
    if message.from_user.id not in verified_admins: verified_admins.append(message.from_user.id)
    bot.reply_to(message, "🔓 Доступ к секретным логам разрешен. Команда: /logs")

@bot.message_handler(commands=['logs'])
def show_logs(message):
    if message.from_user.id in verified_admins:
        bot.send_message(message.chat.id, "📡 ПОСЛЕДНИЕ СОБЫТИЯ:\n" + "\n".join(logs[-10:]))

# --- ГЛАВНЫЙ ПРОЦЕССОР ---
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    uid = message.from_user.id
    text = message.text
    
    # Список всех команд для игнорирования стилями
    commands = ["🎭 Стили текста", "🎬 Анимации", "🛡 Безопасность", "🧹 Удалить мои сообщения", "🔙 Назад", "❌ Сбросить всё",
                "M O N O", "Reverse", "Cyber", "Gothic", "Bubble", "SmallCaps", "Mirror", "Bold", "Underline", "Strike",
                "📡 Передача", "💾 Загрузка", "⌨️ Печать", "🔍 Сканирование", "🔓 Взлом"]

    if text in commands:
        if text == "🔙 Назад": main_menu(message)
        elif text == "❌ Сбросить всё":
            user_styles.pop(uid, None)
            bot.send_message(message.chat.id, "✅ Все настройки сброшены.")
        elif text == "🧹 Удалить мои сообщения":
            if uid in sent_messages:
                for mid in sent_messages[uid]:
                    try: bot.delete_message(message.chat.id, mid)
                    except: pass
                sent_messages[uid] = []
                bot.send_message(message.chat.id, "✅ Ваши сообщения удалены.")
        elif text in commands[6:]:
            user_styles[uid] = text
            bot.send_message(message.chat.id, f"✅ Режим '{text}' включен.")
        return

    if not check_safety(message): return
    logs.append(f"[{datetime.now().strftime('%H:%M')}] {message.from_user.first_name}: {text}")

    if uid in user_styles:
        mode = user_styles[uid]
        bot.delete_message(message.chat.id, message.message_id)
        
        # Блок анимаций
        anim_data = {
            "📡 Передача": ("📡", [".", "..", "..."]),
            "💾 Загрузка": ("💾", [" [▯▯▯▯]", " [▮▯▯▯]", " [▮▮▯▯]", " [▮▮▮▯]", " [▮▮▮▮]"]),
            "⌨️ Печать": ("⌨️", ["|", "_", "√"]),
            "🔍 Сканирование": ("🔍", ["⚡", "🛰", "📡"]),
            "🔓 Взлом": ("🔓", ["****", "###", "@@@", "ACCESS"])
        }

        if mode in anim_data:
            icon, frames = anim_data[mode]
            m = bot.send_message(message.chat.id, f"{icon} {message.from_user.first_name}: {mode}...")
            if uid not in sent_messages: sent_messages[uid] = []
            sent_messages[uid].append(m.message_id)
            
            for f in frames:
                time.sleep(0.3)
                try: bot.edit_message_text(f"{icon} {message.from_user.first_name}: {f}", message.chat.id, m.message_id)
                except: break
            time.sleep(0.2)
            bot.edit_message_text(f"{icon} {message.from_user.first_name}: {text}", message.chat.id, m.message_id)
        else:
            # Обычные стили
            styled = apply_style(text, mode)
            m = bot.send_message(message.chat.id, f"👤 {message.from_user.first_name}: {styled}")
            if uid not in sent_messages: sent_messages[uid] = []
            sent_messages[uid].append(m.message_id)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
