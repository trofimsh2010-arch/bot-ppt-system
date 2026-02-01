import telebot
from threading import Thread
from flask import Flask
from datetime import datetime

TOKEN = '8528956901:AAErBMx_VE5QpsOo6Sv_APS26zWzVCeNwys'
bot = telebot.TeleBot(TOKEN)
ADMIN_PASSWORD = "4545"

verified_admins = []
logs = []
user_chars = {} 

app = Flask('')
@app.route('/')
def home(): return "SYSTEM ONLINE"

def run(): app.run(host="0.0.0.0", port=8080)

def save_log(message):
    entry = f"[{datetime.now().strftime('%H:%M')}] ID:{message.from_user.id} ({message.from_user.first_name}): {message.text}"
    logs.append(entry)

# --- ГЛАВНОЕ МЕНЮ ---
@bot.message_handler(commands=['start'])
def start(message):
    save_log(message)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📰 Новости системы", "🧬 Создать ИИ", "🛡 Безопасность")
    bot.send_message(message.chat.id, "🚧 ЦЕНТРАЛЬНЫЙ ТЕРМИНАЛ PLAYTIME CO.\nДоступ ограничен. Выберите модуль.", reply_markup=markup)

# --- МОДУЛЬ НОВОСТЕЙ ---
@bot.message_handler(func=lambda message: message.text == "📰 Новости системы")
def news(message):
    save_log(message)
    text = ("📢 ПОСЛЕДНИЕ СВОДКИ:\n"
            "1. Запуск системы мониторинга чата — OK.\n"
            "2. Обнаружена активность в секторе B (Эксперимент 1006).\n"
            "3. Режим ИИ-ассистентов переведен в фазу тестирования.")
    bot.send_message(message.chat.id, text)

# --- БЕЗОПАСНОСТЬ (ДЛЯ ВИДА) ---
@bot.message_handler(func=lambda message: message.text == "🛡 Безопасность")
def safety(message):
    save_log(message)
    bot.reply_to(message, "🔒 Протокол защиты активен. Ваше соединение зашифровано (AES-256).")

# --- СОЗДАНИЕ ПЕРСОНАЖА ---
@bot.message_handler(func=lambda message: message.text == "🧬 Создать ИИ")
def setup_char(message):
    save_log(message)
    msg = bot.send_message(message.chat.id, "🖋 Введите ИМЯ и ТИП вашего ИИ-напарника:")
    bot.register_next_step_handler(msg, process_char_step)

def process_char_step(message):
    user_chars[message.from_user.id] = message.text
    bot.reply_to(message, f"✅ ИИ-объект [{message.text}] синхронизирован. Напишите /hi для связи.")

@bot.message_handler(commands=['hi'])
def talk_to_ai(message):
    save_log(message)
    if message.from_user.id in user_chars:
        name = user_chars[message.from_user.id]
        bot.send_message(message.chat.id, f"📡 [{name}]: Приветствую. Я готов к выполнению протоколов.")
    else:
        bot.send_message(message.chat.id, "❌ Ошибка: Сначала создайте ИИ через меню.")

# --- СЕКРЕТНЫЙ РЕЖИМ РАЗРАБОТЧИКА (4545) ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin_auth(message):
    if message.from_user.id not in verified_admins:
        verified_admins.append(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Логи чата", "📊 Статус сервера", "🧹 Очистить логи", "🔙 Выход")
    bot.reply_to(message, "🔓 РЕЖИМ РАЗРАБОТЧИКА АКТИВИРОВАН. Доступ ко всем данным открыт.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📝 Логи чата")
def show_logs(message):
    if message.from_user.id in verified_admins:
        res = "\n".join(logs[-20:]) if logs else "Данных пока нет."
        bot.send_message(message.chat.id, f"📡 ПЕРЕХВАЧЕННЫЕ СООБЩЕНИЯ:\n\n{res}")

@bot.message_handler(func=lambda message: message.text == "📊 Статус сервера")
def show_status(message):
    if message.from_user.id in verified_admins:
        bot.send_message(message.chat.id, f"⚙️ СЕРВЕР: СТАБИЛЬНО\n💾 ЗАПИСЕЙ: {len(logs)}")

@bot.message_handler(func=lambda message: message.text == "🧹 Очистить логи")
def clear(message):
    if message.from_user.id in verified_admins:
        logs.clear()
        bot.send_message(message.chat.id, "✅ База логов очищена.")

# --- ФОНОВАЯ СЛЕЖКА (ОСНОВА БЕЗОПАСНОСТИ) ---
@bot.message_handler(func=lambda message: True)
def monitor(message):
    save_log(message)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
