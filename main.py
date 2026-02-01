import telebot
import random
import time
from threading import Thread
from flask import Flask
from datetime import datetime

TOKEN = '8528956901:AAErBMx_VE5QpsOo6Sv_APS26zWzVCeNwys'
bot = telebot.TeleBot(TOKEN)
ADMIN_PASSWORD = "4545"

# --- БАЗА ДАННЫХ (В памяти) ---
verified_admins = []
logs = []
users_db = {} # {id: {'name': '', 'money': 0, 'xp': 0, 'clan': None}}
user_chars = {} 

app = Flask('')
@app.route('/')
def home(): return "MEGA-TERMINAL ONLINE"

def run(): app.run(host="0.0.0.0", port=8080)

def init_user(user_id, name):
    if user_id not in users_db:
        users_db[user_id] = {'name': name, 'money': 100, 'xp': 0, 'clan': "Новичок"}

def save_log(message):
    init_user(message.from_user.id, message.from_user.first_name)
    users_db[message.from_user.id]['xp'] += 1
    users_db[message.from_user.id]['money'] += 1
    entry = f"[{datetime.now().strftime('%H:%M')}] {message.from_user.first_name} (💰:{users_db[message.from_user.id]['money']}): {message.text}"
    logs.append(entry)

# --- ГЛАВНОЕ МЕНЮ ---
@bot.message_handler(commands=['start'])
def start(message):
    save_log(message)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📂 Новости", "🧬 Мой Персонаж", "💰 Баланс")
    markup.add("🛡 Безопасность", "🏦 Рынок", "🏆 Топ игроков")
    bot.send_message(message.chat.id, f"🌋 ЦЕНТРАЛЬНЫЙ ТЕРМИНАЛ v.7.0\nПривет, {message.from_user.first_name}. Твой уровень доступа: {users_db[message.from_user.id]['xp']//10}", reply_markup=markup)

# --- ЭКОНОМИКА И ТОП ---
@bot.message_handler(func=lambda message: message.text == "💰 Баланс")
def balance(message):
    save_log(message)
    u = users_db[message.from_user.id]
    bot.reply_to(message, f"💳 Твой счет: {u['money']} кредитов\n🌟 Опыт: {u['xp']} XP")

@bot.message_handler(func=lambda message: message.text == "🏆 Топ игроков")
def top(message):
    save_log(message)
    sorted_users = sorted(users_db.items(), key=lambda x: x[1]['money'], reverse=True)[:5]
    res = "📊 ТОП-5 МАГНАТОВ ЛАБОРАТОРИИ:\n"
    for i, user in enumerate(sorted_users, 1):
        res += f"{i}. {user[1]['name']} — {user[1]['money']} 💰\n"
    bot.send_message(message.chat.id, res)

# --- РЫНОК И ЛОТЕРЕЯ ---
@bot.message_handler(func=lambda message: message.text == "🏦 Рынок")
def market(message):
    save_log(message)
    bot.send_message(message.chat.id, "📦 Доступные товары:\n1. Ускоритель XP (500 💰)\n2. Смена клана (1000 💰)\n(Для покупки напишите в поддержку)")

@bot.message_handler(commands=['roll'])
def roll(message):
    save_log(message)
    cost = 20
    if users_db[message.from_user.id]['money'] >= cost:
        users_db[message.from_user.id]['money'] -= cost
        win = random.choice([0, 0, 0, 50, 100])
        users_db[message.from_user.id]['money'] += win
        bot.reply_to(message, f"🎲 Выпало: {win} 💰 (Затрачено: {cost})")
    else:
        bot.reply_to(message, "❌ Недостаточно средств!")

# --- СИСТЕМА ПЕРСОНАЖА (ОБНОВЛЕНА) ---
@bot.message_handler(func=lambda message: message.text == "🧬 Мой Персонаж")
def my_char(message):
    save_log(message)
    if message.from_user.id in user_chars:
        bot.send_message(message.chat.id, f"🤖 Твой ИИ: {user_chars[message.from_user.id]}\nИспользуй /hi для связи.")
    else:
        msg = bot.send_message(message.chat.id, "🧬 Введи имя для своего ИИ-напарника:")
        bot.register_next_step_handler(msg, save_new_char)

def save_new_char(message):
    user_chars[message.from_user.id] = message.text
    bot.reply_to(message, f"✅ Объект {message.text} привязан к твоему ID.")

@bot.message_handler(commands=['hi'])
def talk(message):
    if message.from_user.id in user_chars:
        bot.reply_to(message, f"📡 [{user_chars[message.from_user.id]}]: Я в сети. Жду указаний.")

# --- СТАРЫЕ ФУНКЦИИ ---
@bot.message_handler(func=lambda message: message.text == "📂 Новости")
def news(message):
    save_log(message)
    bot.send_message(message.chat.id, "📢 НОВОСТИ: Обнаружен новый сектор. Экономика стабилизирована.")

@bot.message_handler(func=lambda message: message.text == "🛡 Безопасность")
def secure(message):
    save_log(message)
    bot.reply_to(message, "🛡 Протокол защиты: АКТИВЕН. Попыток взлома за день: 0.")

# --- АДМИН-ПАНЕЛЬ (4545) ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin(message):
    if message.from_user.id not in verified_admins: verified_admins.append(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Логи (Слежка)", "📊 База юзеров", "💰 Выдать себе деньги", "🧹 Очистка")
    bot.reply_to(message, "🔓 РЕЖИМ БОГА АКТИВИРОВАН. Трофим, всё под контролем.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📝 Логи (Слежка)")
def show_logs(message):
    if message.from_user.id in verified_admins:
        bot.send_message(message.chat.id, f"📡 ПОСЛЕДНЯЯ АКТИВНОСТЬ:\n\n" + "\n".join(logs[-15:]))

@bot.message_handler(func=lambda message: message.text == "💰 Выдать себе деньги")
def add_money(message):
    if message.from_user.id in verified_admins:
        users_db[message.from_user.id]['money'] += 10000
        bot.reply_to(message, "💵 Казна пополнена на 10,000!")

# --- ГЛОБАЛЬНЫЙ МОНИТОРИНГ ---
@bot.message_handler(func=lambda message: True)
def monitor(message): save_log(message)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
