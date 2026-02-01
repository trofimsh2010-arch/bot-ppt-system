import telebot
import time
import random
from threading import Thread
from flask import Flask
from datetime import datetime

# Твой токен
TOKEN = '8528956901:AAErBMx_VE5QpsOo6Sv_APS26zWzVCeNwys'
bot = telebot.TeleBot(TOKEN)
ADMIN_PASSWORD = "4545"

# Базы данных
verified_admins = []
logs = []
user_styles = {} 
last_msg_time = {}
sent_messages = {}

# Список запрещенных слов (дополняй по нужде)
BAD_WORDS = ["мат1", "порно", "18+", "хентай", "спам"]

app = Flask('')
@app.route('/')
def home(): return "GROUP_SYSTEM_ONLINE"

def run(): app.run(host="0.0.0.0", port=8080)

# --- МОДУЛЬ БЕЗОПАСНОСТИ ---
def check_safety(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    text = message.text.lower() if message.text else ""
    now = time.time()

    # 1. Анти-спам
    if uid in last_msg_time and now - last_msg_time[uid] < 0.7:
        try: bot.delete_message(chat_id, message.message_id)
        except: pass
        return False
    last_msg_time[uid] = now
    
    # 2. Фильтр контента
    if any(word in text for word in BAD_WORDS):
        try:
            bot.delete_message(chat_id, message.message_id)
            bot.send_message(chat_id, f"⚠️ @{message.from_user.username or message.from_user.first_name}, сообщение удалено: Нарушение безопасности.")
        except: pass
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
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎭 Стили текста", "🎬 Анимации")
    markup.add("🛡 Безопасность", "🧹 Удалить мои сообщения")
    markup.add("❌ Сбросить всё")
    bot.send_message(message.chat.id, "💻 **ТЕРМИНАЛ v.24.0 (Групповой режим)**\nВыберите модуль управления:", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🛡 Безопасность")
def security_status(message):
    status = "🛡 **СТАТУС ЗАЩИТЫ ЧАТА**\n✅ Фильтры активны в группах\n✅ Удаление оригиналов включено"
    bot.send_message(message.chat.id, status, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🎬 Анимации")
def anim_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📡 Передача", "💾 Загрузка", "⌨️ Печать", "🔍 Сканирование", "🔓 Взлом")
    markup.add("🔙 Назад")
    bot.send_message(message.chat.id, "Выберите анимацию:", reply_markup=markup)

# --- АДМИНКА ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin_login(message):
    verified_admins.append(message.from_user.id)
    bot.reply_to(message, "🔓 Доступ к логам разрешен. (/logs)")

@bot.message_handler(commands=['logs'])
def show_logs(message):
    if message.from_user.id in verified_admins:
        bot.send_message(message.chat.id, "📡 ЛОГИ:\n" + "\n".join(logs[-10:]))

# --- ОСНОВНОЙ ОБРАБОТЧИК ---
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    text = message.text
    
    # Список системных кнопок
    sys_btns = ["🎭 Стили текста", "🎬 Анимации", "🛡 Безопасность", "🧹 Удалить мои сообщения", "🔙 Назад", "❌ Сбросить всё",
                "M O N O", "Reverse", "Cyber", "Gothic", "Bubble", "SmallCaps", "Mirror", "Bold", "Underline", "Strike",
                "📡 Передача", "💾 Загрузка", "⌨️ Печать", "🔍 Сканирование", "🔓 Взлом"]

    if text in sys_btns:
        if text == "🔙 Назад": start(message)
        elif text == "❌ Сбросить всё":
            user_styles.pop(uid, None)
            bot.send_message(chat_id, "✅ Настройки очищены.")
        elif text == "🧹 Удалить мои сообщения":
            if uid in sent_messages:
                for mid in sent_messages[uid]:
                    try: bot.delete_message(chat_id, mid)
                    except: pass
                sent_messages[uid] = []
        elif text in sys_btns[6:]:
            user_styles[uid] = text
            bot.send_message(chat_id, f"✅ Режим '{text}' активен.")
        return

    # Проверка безопасности
    if not check_safety(message): return
    
    logs.append(f"[{datetime.now().strftime('%H:%M')}] {message.from_user.first_name}: {text}")

    # Если включен стиль/анимация
    if uid in user_styles:
        mode = user_styles[uid]
        try: bot.delete_message(chat_id, message.message_id) # Удаляем оригинал юзера
        except: pass
        
        user_name = message.from_user.first_name
        
        # Анимации
        anim_data = {
            "📡 Передача": ("📡", [".", "..", "..."]),
            "💾 Загрузка": ("💾", ["▯", "▮", "■"]),
            "⌨️ Печать": ("⌨️", ["|", "_"]),
            "🔍 Сканирование": ("🔍", ["⚡", "🛰"]),
            "🔓 Взлом": ("🔓", ["***", "ACCESS"])
        }

        if mode in anim_data:
            icon, frames = anim_data[mode]
            m = bot.send_message(chat_id, f"{icon} {user_name}: {mode}...")
            if uid not in sent_messages: sent_messages[uid] = []
            sent_messages[uid].append(m.message_id)
            
            for f in frames:
                time.sleep(0.3)
                try: bot.edit_message_text(f"{icon} {user_name}: {f}", chat_id, m.message_id)
                except: break
            bot.edit_message_text(f"{icon} {user_name}: {text}", chat_id, m.message_id)
        else:
            # Обычные стили
            styled = apply_style(text, mode)
            m = bot.send_message(chat_id, f"👤 {user_name}: {styled}")
            if uid not in sent_messages: sent_messages[uid] = []
            sent_messages[uid].append(m.message_id)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
