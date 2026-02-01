import telebot
import random
from threading import Thread
from flask import Flask
from datetime import datetime

TOKEN = '8528956901:AAErBMx_VE5QpsOo6Sv_APS26zWzVCeNwys'
bot = telebot.TeleBot(TOKEN)
ADMIN_PASSWORD = "4545"

verified_admins = []
logs = []

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
    bot.send_message(message.chat.id, "🌋 Добро пожаловать в Playtime Co.\n\nДоступные модули: /games\nДля авторизации введите сервисный код.")

@bot.message_handler(commands=['games'])
def games_list(message):
    save_log(message)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔮 Предсказание", "⚖️ Тест на удачу")
    bot.send_message(message.chat.id, "🎮 Выберите развлекательный модуль:", reply_markup=markup)

# --- ИГРЫ (ПРИКРЫТИЕ) ---
@bot.message_handler(func=lambda message: message.text == "🔮 Предсказание")
def crystal(message):
    ans = ["Да", "Нет", "Возможно", "Никогда"]
    bot.reply_to(message, f"🔮 Ответ: {random.choice(ans)}")

@bot.message_handler(func=lambda message: message.text == "⚖️ Тест на удачу")
def luck(message):
    score = random.randint(0, 100)
    bot.reply_to(message, f"🍀 Удача: {score}%")

# --- СЕКРЕТНЫЙ ВХОД 4545 ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin_mode(message):
    if message.from_user.id not in verified_admins:
        verified_admins.append(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📊 Статус", "📝 Логи", "🧹 Очистить")
    bot.reply_to(message, "🔓 ДОСТУП РАЗРЕШЕН. Админ-кнопки активированы.", reply_markup=markup)

# --- УПРАВЛЕНИЕ (БЕЗ ПОВТОРНОГО ПАРОЛЯ) ---
@bot.message_handler(func=lambda message: message.text == "📝 Логи")
def show_logs(message):
    if message.from_user.id in verified_admins:
        res = "\n".join(logs[-25:]) if logs else "Логов пока нет."
        bot.send_message(message.chat.id, f"📡 АКТИВНОСТЬ:\n\n{res}")

@bot.message_handler(func=lambda message: message.text == "📊 Статус")
def show_status(message):
    if message.from_user.id in verified_admins:
        bot.send_message(message.chat.id, f"⚙️ Статус: OK\n📊 Сообщений в базе: {len(logs)}")

@bot.message_handler(func=lambda message: message.text == "🧹 Очистить")
def clear(message):
    if message.from_user.id in verified_admins:
        logs.clear()
        bot.send_message(message.chat.id, "✅ База очищена.")

# --- СЛЕЖКА ЗА ВСЕМИ ---
@bot.message_handler(func=lambda message: True)
def monitor(message):
    save_log(message)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
