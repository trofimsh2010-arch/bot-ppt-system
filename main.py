import telebot
import random
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
users_db = {} 
user_chars = {} 
last_msg_time = {} 

BAD_WORDS = ["мат1", "порно", "18+"] 
SURVEY_QUESTIONS = ["Оцените сектор B?", "Готовы к тестам?", "Как ваш питомец?"]

app = Flask('')
@app.route('/')
def home(): return "ANIMATION_SYSTEM_ONLINE"

def run(): app.run(host="0.0.0.0", port=8080)

def init_user(uid, name):
    if uid not in users_db:
        users_db[uid] = {'name': name, 'money': 500, 'loan': 0, 'status': 'Сотрудник'}

def check_safety(message):
    uid = message.from_user.id
    text = message.text.lower() if message.text else ""
    now = time.time()
    if uid in last_msg_time and now - last_msg_time[uid] < 1.2:
        bot.delete_message(message.chat.id, message.message_id)
        return False
    last_msg_time[uid] = now
    if any(word in text for word in BAD_WORDS):
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "⚠️ Нарушение протокола (Мат/18+).")
        return False
    return True

def save_log(message):
    init_user(message.from_user.id, message.from_user.first_name)
    logs.append(f"[{datetime.now().strftime('%H:%M')}] {message.from_user.first_name}: {message.text}")

@bot.message_handler(commands=['start'])
def start(message):
    if not check_safety(message): return
    save_log(message)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🧬 Мой Питомец", "💰 Баланс", "📋 Пройти опрос")
    markup.add("🏪 Магазин", "💳 Взять Кредит")
    bot.send_message(message.chat.id, "🛡 ТЕРМИНАЛ v.13.0\nВсе системы защиты и анимации активны.", reply_markup=markup)

# --- НОВАЯ ФУНКЦИЯ: АНИМИРОВАННЫЙ ТЕКСТ ---
@bot.message_handler(func=lambda message: message.text.lower() == "анимация")
def buy_anim(message):
    uid = message.from_user.id
    if users_db[uid]['money'] >= 3000:
        users_db[uid]['money'] -= 3000
        msg = bot.send_message(message.chat.id, "🎬 Инициализация анимации...")
        frames = ["🔸 ЗАГРУЗКА 🔸", "🔹 ЗАГРУЗКА 🔹", "🔸 ЗАГРУЗКА 🔸", "🚀 СТАТУС: ACTIVE", "✨ СТАТУС: ONLINE ✨"]
        for frame in frames:
            try:
                bot.edit_message_text(frame, message.chat.id, msg.message_id)
                time.sleep(1)
            except: break
        bot.send_message(message.chat.id, "✅ Эффект применен успешно.")
    else: bot.reply_to(message, "❌ Нужно 3000 💰")

# --- СТАРЫЕ ФУНКЦИИ (ОПРОСЫ, ПЕРСОНАЖ, МАГАЗИН) ---
@bot.message_handler(func=lambda message: message.text == "🏪 Магазин")
def shop(message):
    bot.send_message(message.chat.id, "🛒 МАГАЗИН:\n1. Анимация (3000 💰)\n2. Анонимка (500 💰)\nНапишите название.")

@bot.message_handler(func=lambda message: message.text == "📋 Пройти опрос")
def survey(message):
    if not check_safety(message): return
    q = random.choice(SURVEY_QUESTIONS)
    msg = bot.send_message(message.chat.id, f"📝 {q}")
    bot.register_next_step_handler(msg, lambda m: bot.send_message(m.chat.id, f"✅ +{random.randint(200, 400)} 💰") or users_db[m.from_user.id].update({'money': users_db[m.from_user.id]['money']+300}))

@bot.message_handler(func=lambda message: message.text == "🧬 Мой Питомец")
def pet(message):
    msg = bot.send_message(message.chat.id, "🧬 Имя ИИ-питомца:")
    bot.register_next_step_handler(msg, lambda m: user_chars.update({m.from_user.id: {'name': m.text, 'trait': 'добрый'}}) or bot.reply_to(m, "✨ Готов! /hi"))

@bot.message_handler(commands=['hi'])
def hi(message):
    if message.from_user.id in user_chars:
        bot.send_message(message.chat.id, f"📡 [{user_chars[message.from_user.id]['name']}]: Привет!")
    else: bot.reply_to(message, "Создай через 🧬")

@bot.message_handler(func=lambda message: message.text == "💰 Баланс")
def balance(message):
    u = users_db[message.from_user.id]
    bot.reply_to(message, f"💵 Кредиты: {u['money']} | Долг: {u['loan']}")

# --- АДМИНКА (4545) ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin(message):
    if message.from_user.id not in verified_admins: verified_admins.append(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Логи", "💰 Дать денег", "🔙 Назад")
    bot.reply_to(message, "🔓 ДОСТУП РАЗРЕШЕН, ТРОФИМ.")

@bot.message_handler(func=lambda message: message.text == "📝 Логи")
def show_logs(message):
    if message.from_user.id in verified_admins:
        bot.send_message(message.chat.id, "📡 ПЕРЕХВАТ:\n" + "\n".join(logs[-10:]))

@bot.message_handler(func=lambda message: True)
def monitor(message):
    if check_safety(message): save_log(message)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
