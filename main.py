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

# Настройки безопасности
BAD_WORDS = ["мат1", "порно", "18+"]

app = Flask('')
@app.route('/')
def home(): return "SECURE_TERMINAL_ONLINE"

def run(): app.run(host="0.0.0.0", port=8080)

def check_safety(message):
    uid = message.from_user.id
    text = message.text.lower() if message.text else ""
    now = time.time()
    # Анти-спам
    if uid in last_msg_time and now - last_msg_time[uid] < 1.0:
        bot.delete_message(message.chat.id, message.message_id)
        return False
    last_msg_time[uid] = now
    # Фильтр матов
    if any(word in text for word in BAD_WORDS):
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "⚠️ Нарушение протокола. Сообщение стерто.")
        return False
    return True

def apply_style(text, style):
    if style == "M O N O":
        return f"`{' '.join(text.upper())}`"
    elif style == "Квадраты":
        return f"[{text}]"
    elif style == "Анимация":
        return f"📡 {text}..." # База для анимации
    return text

@bot.message_handler(commands=['start'])
def start(message):
    if not check_safety(message): return
    logs.append(f"[{datetime.now().strftime('%H:%M')}] {message.from_user.first_name} запустил систему.")
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎭 Выбрать стиль текста", "🎬 Анимация")
    
    welcome_text = (
        "💻 **ТЕРМИНАЛ PLAYTIME Co.**\n"
        "--------------------------\n"
        "Статус: Активен. Все развлекательные модули удалены.\n"
        "Функционал разработан ИИ Джемини.\n"
        "Доступ к логам закрыт на пароль.\n"
        "--------------------------"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# --- СИСТЕМА СТИЛЕЙ ---
@bot.message_handler(func=lambda message: message.text == "🎭 Выбрать стиль текста")
def style_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("M O N O", "Квадраты", "Обычный")
    bot.send_message(message.chat.id, "Выберите стиль кодирования сообщений:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["M O N O", "Квадраты", "Обычный"])
def set_style(message):
    user_styles[message.from_user.id] = message.text
    bot.send_message(message.chat.id, f"✅ Стиль '{message.text}' установлен.")

@bot.message_handler(func=lambda message: message.text == "🎬 Анимация")
def anim_status(message):
    user_styles[message.from_user.id] = "Анимация"
    bot.send_message(message.chat.id, "✅ Режим анимированной передачи включен.")

# --- АДМИНКА (4545) ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin(message):
    if message.from_user.id not in verified_admins: 
        verified_admins.append(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Просмотр логов", "🧹 Очистить", "🔙 Выход")
    bot.reply_to(message, "🔓 ДОСТУП В ЯДРО РАЗРЕШЕН. ТРОФИМ, СЛУШАЮ.")

@bot.message_handler(func=lambda message: message.text == "📝 Просмотр логов")
def show_logs(message):
    if message.from_user.id in verified_admins:
        res = "\n".join(logs[-15:]) if logs else "Логов нет."
        bot.send_message(message.chat.id, f"📡 ПОЛНЫЙ ПЕРЕХВАТ:\n\n{res}")

# --- ГЛОБАЛЬНЫЙ ОБРАБОТЧИК (СТИЛИ И ЛОГИ) ---
@bot.message_handler(func=lambda message: True)
def monitor(message):
    if not check_safety(message): return
    
    uid = message.from_user.id
    logs.append(f"[{datetime.now().strftime('%H:%M')}] {message.from_user.first_name}: {message.text}")
    
    # Если у пользователя выбран стиль, переотправляем анимированно или стилизованно
    if uid in user_styles and user_styles[uid] != "Обычный":
        styled_text = apply_style(message.text, user_styles[uid])
        
        if user_styles[uid] == "Анимация":
            msg = bot.send_message(message.chat.id, "📡 Кодирование...")
            frames = [f"📡 {message.text}.", f"📡 {message.text}..", f"📡 {message.text}..."]
            for frame in frames:
                try:
                    time.sleep(0.5)
                    bot.edit_message_text(frame, message.chat.id, msg.message_id)
                except: break
        else:
            bot.send_message(message.chat.id, styled_text, parse_mode="Markdown")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
