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
user_styles = {} # {id: 'style_name'}
last_msg_time = {}

BAD_WORDS = ["мат1", "порно", "18+", "хентай"]

app = Flask('')
@app.route('/')
def home(): return "ULTIMATE_SECURITY_ONLINE"

def run(): app.run(host="0.0.0.0", port=8080)

# --- МОДУЛЬ БЕЗОПАСНОСТИ ---
def check_safety(message):
    uid = message.from_user.id
    text = message.text.lower() if message.text else ""
    now = time.time()
    
    # 1. Анти-спам
    if uid in last_msg_time and now - last_msg_time[uid] < 1.0:
        bot.delete_message(message.chat.id, message.message_id)
        return False
    last_msg_time[uid] = now
    
    # 2. Фильтр контента
    if any(word in text for word in BAD_WORDS):
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, f"⚠️ Нарушение безопасности, {message.from_user.first_name}. Сообщение стерто.")
        return False
    return True

# --- ОБРАБОТКА СТИЛЕЙ ---
def apply_style(text, style):
    if style == "M O N O":
        return f"{' '.join(text.upper())}"
    elif style == "Reverse":
        return text[::-1]
    elif style == "Cyber":
        return f"01_{text.replace(' ', '_')}_10"
    elif style == "Gothic":
        return f"𝔊𝔬𝔱𝔥𝔦𝔠: {text}"
    return text

@bot.message_handler(commands=['start'])
def start(message):
    if not check_safety(message): return
    main_menu(message)

def main_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎭 Стили текста", "🎬 Анимации")
    markup.add("🛠 Статус системы")
    
    text = (
        "💻 **ТЕРМИНАЛ PLAYTIME Co. v.18.0**\n"
        "--------------------------\n"
        "Функции: ИИ Джемини\n"
        "Безопасность: ВЫСОКАЯ\n"
        "--------------------------"
    )
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# --- МЕНЮ СТИЛЕЙ ---
@bot.message_handler(func=lambda message: message.text == "🎭 Стили текста")
def style_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("M O N O", "Reverse", "Cyber", "Gothic")
    markup.add("❌ Сбросить стиль", "🔙 Назад")
    bot.send_message(message.chat.id, "Выберите стиль кодирования:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🎬 Анимации")
def anim_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📡 Передача", "💾 Загрузка данных")
    markup.add("🔙 Назад")
    bot.send_message(message.chat.id, "Выберите тип анимации:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["M O N O", "Reverse", "Cyber", "Gothic", "📡 Передача", "💾 Загрузка данных"])
def set_style(message):
    user_styles[message.from_user.id] = message.text
    bot.reply_to(message, f"✅ Установлен режим: {message.text}")

@bot.message_handler(func=lambda message: message.text == "❌ Сбросить стиль")
def reset_style(message):
    user_styles.pop(message.from_user.id, None)
    bot.reply_to(message, "✅ Стиль сброшен к обычному.")

@bot.message_handler(func=lambda message: message.text == "🔙 Назад")
def back_to_start(message):
    main_menu(message)

# --- АДМИНКА (4545) ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin(message):
    verified_admins.append(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Логи", "🧹 Очистить", "🔙 Назад")
    bot.reply_to(message, "🔓 ЯДРО ВСКРЫТО. СЛУШАЮ, ТРОФИМ.")

@bot.message_handler(func=lambda message: message.text == "📝 Логи")
def show_logs(message):
    if message.from_user.id in verified_admins:
        res = "\n".join(logs[-15:]) if logs else "Нет записей."
        bot.send_message(message.chat.id, f"📡 ПЕРЕХВАТ СООБЩЕНИЙ:\n\n{res}")

# --- ГЛОБАЛЬНЫЙ ПРОЦЕССОР ---
@bot.message_handler(func=lambda message: True)
def process_all(message):
    if not check_safety(message): return
    
    uid = message.from_user.id
    name = message.from_user.first_name
    logs.append(f"[{datetime.now().strftime('%H:%M')}] {name}: {message.text}")
    
    # Если у юзера активен стиль или анимация
    if uid in user_styles:
        style = user_styles[uid]
        bot.delete_message(message.chat.id, message.message_id) # Удаляем оригинал
        
        if style in ["📡 Передача", "💾 Загрузка данных"]:
            m_id = bot.send_message(message.chat.id, f"🌀 {name}: Подключение...").message_id
            frames = [f" {name}: {message.text}.", f" {name}: {message.text}..", f" {name}: {message.text}..."]
            for frame in frames:
                time.sleep(0.4)
                try: bot.edit_message_text(f"{'📡' if style=='📡 Передача' else '💾'} {frame}", message.chat.id, m_id)
                except: break
        else:
            final_text = apply_style(message.text, style)
            bot.send_message(message.chat.id, f"👤 {name}: {final_text}")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
