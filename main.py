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
sent_messages = {}

BAD_WORDS = ["мат1", "порно", "18+", "хентай"]

app = Flask('')
@app.route('/')
def home(): return "SYSTEM_ACTIVE_SECURE"

def run(): app.run(host="0.0.0.0", port=8080)

# --- БЕЗОПАСНОСТЬ ---
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
        bot.send_message(message.chat.id, "⚠️ Сообщение заблокировано фильтром безопасности.")
        return False
    return True

# --- СТИЛИ ---
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

@bot.message_handler(commands=['start'])
def start(message):
    if not check_safety(message): return
    main_menu(message)

def main_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎭 Стили текста", "🎬 Анимации")
    markup.add("🧹 Удалить мои сообщения", "❌ Сбросить стиль")
    bot.send_message(message.chat.id, "💻 **ЦЕНТРАЛЬНЫЙ ТЕРМИНАЛ v.22.0**\nВсе системы защиты активны.\nАвтор функций: ИИ Джемини.", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🎭 Стили текста")
def style_menu(message):
    if not check_safety(message): return
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("M O N O", "Reverse", "Cyber", "Gothic", "Bubble")
    markup.add("SmallCaps", "Mirror", "Bold", "Underline", "Strike")
    markup.add("🔙 Назад")
    bot.send_message(message.chat.id, "Выберите режим отображения:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🎬 Анимации")
def anim_menu(message):
    if not check_safety(message): return
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📡 Передача", "💾 Загрузка", "🔙 Назад")
    bot.send_message(message.chat.id, "Выберите тип анимации данных:", reply_markup=markup)

# --- АДМИНИСТРИРОВАНИЕ ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin_login(message):
    if message.from_user.id not in verified_admins: verified_admins.append(message.from_user.id)
    bot.reply_to(message, "🔓 ДОСТУП В ЯДРО СИСТЕМЫ РАЗРЕШЕН. Команда: /logs")

@bot.message_handler(commands=['logs'])
def show_logs(message):
    if message.from_user.id in verified_admins:
        res = "\n".join(logs[-15:]) if logs else "Данные отсутствуют."
        bot.send_message(message.chat.id, f"📡 ПЕРЕХВАТ ТЕРМИНАЛА:\n\n{res}")

# --- ОБРАБОТЧИК СООБЩЕНИЙ ---
@bot.message_handler(func=lambda message: True)
def global_handler(message):
    uid = message.from_user.id
    text = message.text
    
    # Исключаем системные команды из стилизации
    system_buttons = [
        "🎭 Стили текста", "🎬 Анимации", "🔙 Назад", "❌ Сбросить стиль", 
        "🧹 Удалить мои сообщения", "M O N O", "Reverse", "Cyber", "Gothic", 
        "Bubble", "SmallCaps", "Mirror", "Bold", "Underline", "Strike",
        "📡 Передача", "💾 Загрузка"
    ]
    
    if text in system_buttons:
        if text == "🔙 Назад": main_menu(message)
        elif text == "❌ Сбросить стиль":
            user_styles.pop(uid, None)
            bot.send_message(message.chat.id, "✅ Стили отключены.")
        elif text == "🧹 Удалить мои сообщения":
            if uid in sent_messages:
                for m_id in sent_messages[uid]:
                    try: bot.delete_message(message.chat.id, m_id)
                    except: pass
                sent_messages[uid] = []
                bot.send_message(message.chat.id, "✅ История ваших сообщений стерта.")
        elif text in system_buttons[5:]:
            user_styles[uid] = text
            bot.send_message(message.chat.id, f"✅ Режим '{text}' активен.")
        return

    if not check_safety(message): return
    logs.append(f"[{datetime.now().strftime('%H:%M')}] {message.from_user.first_name}: {text}")

    if uid in user_styles:
        style = user_styles[uid]
        bot.delete_message(message.chat.id, message.message_id)
        
        if style in ["📡 Передача", "💾 Загрузка"]:
            icon = "📡" if style == "📡 Передача" else "💾"
            m = bot.send_message(message.chat.id, f"{icon} {message.from_user.first_name}: ...")
            if uid not in sent_messages: sent_messages[uid] = []
            sent_messages[uid].append(m.message_id)
            
            for frame in [".", "..", "...", text]:
                time.sleep(0.4)
                try: bot.edit_message_text(f"{icon} {message.from_user.first_name}: {frame}", message.chat.id, m.message_id)
                except: break
        else:
            final = apply_style(text, style)
            m = bot.send_message(message.chat.id, f"👤 {message.from_user.first_name}: {final}")
            if uid not in sent_messages: sent_messages[uid] = []
            sent_messages[uid].append(m.message_id)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
