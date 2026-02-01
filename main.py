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
users_db = {} # {id: {'money': 100, 'loan': 0, 'last_work': 0}}
user_chars = {} # {id: {'name': 'Имя', 'trait': 'Характер', 'mood': 100}}

app = Flask('')
@app.route('/')
def home(): return "ECONOMY_SYSTEM_ONLINE"

def run(): app.run(host="0.0.0.0", port=8080)

def init_user(uid):
    if uid not in users_db:
        users_db[uid] = {'money': 100, 'loan': 0, 'last_work': 0}

def save_log(message):
    uid = message.from_user.id
    init_user(uid)
    users_db[uid]['money'] += random.randint(1, 3) # Начисление за активность
    entry = f"[{datetime.now().strftime('%H:%M')}] {message.from_user.first_name}: {message.text}"
    logs.append(entry)

@bot.message_handler(commands=['start'])
def start(message):
    save_log(message)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🧬 Мой Питомец", "💰 Баланс", "⛏ Работать")
    markup.add("🏪 Магазин", "💳 Взять Кредит", "🛡 Защита")
    bot.send_message(message.chat.id, "🤖 ТЕРМИНАЛ PLAYTIME Co. v.9.0\nЭкономика запущена. Зарабатывайте кредиты для развития питомца.", reply_markup=markup)

# --- ЭКОНОМИКА (РАБОТА И КРЕДИТ) ---
@bot.message_handler(func=lambda message: message.text == "⛏ Работать")
def work(message):
    uid = message.from_user.id
    now = time.time()
    if now - users_db[uid]['last_work'] > 60: # Раз в минуту для теста (можно сменить на 900)
        earned = random.randint(50, 150)
        users_db[uid]['money'] += earned
        users_db[uid]['last_work'] = now
        bot.reply_to(message, f"⚒ Вы отработали смену в шахте. Получено: {earned} 💰")
    else:
        bot.reply_to(message, "⏳ Вы устали. Отдохните еще немного.")

@bot.message_handler(func=lambda message: message.text == "💳 Взять Кредит")
def get_loan(message):
    uid = message.from_user.id
    if users_db[uid]['loan'] == 0:
        users_db[uid]['money'] += 500
        users_db[uid]['loan'] = 600 # Возврат с процентом
        bot.reply_to(message, "🏦 Вам выдано 500 💰. Долг к возврату: 600 💰 (списывается автоматически).")
    else:
        bot.reply_to(message, "❌ У вас уже есть непогашенный кредит!")

@bot.message_handler(func=lambda message: message.text == "💰 Баланс")
def balance(message):
    uid = message.from_user.id
    u = users_db[uid]
    bot.reply_to(message, f"💵 Баланс: {u['money']} 💰\n🏛 Долг: {u['loan']} 💰")

# --- МАГАЗИН (КУДА ТРАТИТЬ) ---
@bot.message_handler(func=lambda message: message.text == "🏪 Магазин")
def shop(message):
    text = ("🛒 МАГАЗИН ТЕХНОЛОГИЙ:\n"
            "1. 🍖 Корм (100 💰) — улучшить настроение питомца.\n"
            "2. ⚡️ Ускоритель (500 💰) — бонус к работе.\n"
            "3. 🎲 Лотерея (200 💰) — шанс выиграть 1000.\n"
            "Для покупки просто напиши название товара (например: Корм)")
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: message.text.lower() == "корм")
def buy_food(message):
    uid = message.from_user.id
    if users_db[uid]['money'] >= 100:
        users_db[uid]['money'] -= 100
        if uid in user_chars:
            user_chars[uid]['mood'] = 100
            bot.reply_to(message, "🍖 Вы покормили питомца. Он больше не будет обижаться какое-то время!")
        else: bot.reply_to(message, "У вас нет питомца.")
    else: bot.reply_to(message, "Недостаточно денег.")

# --- ЖИВОЙ ПИТОМЕЦ (СТАРЫЕ ФУНКЦИИ + НАСТРОЕНИЕ) ---
@bot.message_handler(func=lambda message: message.text == "🧬 Мой Питомец")
def my_char(message):
    save_log(message)
    msg = bot.send_message(message.chat.id, "🧬 Введи ИМЯ питомца:")
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    user_chars[message.from_user.id] = {'name': message.text, 'mood': 100}
    msg = bot.send_message(message.chat.id, "Принято. Каков его ХАРАКТЕР? (злой, добрый, обидчивый):")
    bot.register_next_step_handler(msg, process_trait)

def process_trait(message):
    user_chars[message.from_user.id]['trait'] = message.text.lower()
    bot.reply_to(message, "✨ Питомец готов. Используй /hi")

@bot.message_handler(commands=['hi'])
def talk(message):
    save_log(message)
    uid = message.from_user.id
    if uid in user_chars:
        char = user_chars[uid]
        if char['mood'] < 30:
            bot.send_message(message.chat.id, f"📡 [{char['name']}]: *игнорирует вас, потому что голоден*")
        else:
            char['mood'] -= 5 # Каждое общение тратит силы
            ans = ["Привет!", "Я тут!", "Чего хочешь?"] if char['trait'] == "добрый" else ["М-м?", "Что надо?"]
            bot.send_message(message.chat.id, f"📡 [{char['name']}]: {random.choice(ans)}")
    else: bot.send_message(message.chat.id, "Создай питомца 🧬")

# --- АДМИНКА (4545) ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin(message):
    if message.from_user.id not in verified_admins: verified_admins.append(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Логи чата", "🧹 Очистить", "💰 Чит на деньги")
    bot.reply_to(message, "🔓 ДОСТУП АКТИВИРОВАН.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📝 Логи чата")
def show_logs(message):
    if message.from_user.id in verified_admins:
        bot.send_message(message.chat.id, "📡 ПЕРЕХВАТ:\n" + "\n".join(logs[-10:]))

@bot.message_handler(func=lambda message: True)
def monitor(message): save_log(message)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
