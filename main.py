import telebot
import random
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
user_chars = {} # {id: {'name': 'Имя', 'trait': 'Характер'}}

app = Flask('')
@app.route('/')
def home(): return "SYSTEM ONLINE"

def run(): app.run(host="0.0.0.0", port=8080)

def save_log(message):
    uid = message.from_user.id
    if uid not in users_db:
        users_db[uid] = {'name': message.from_user.first_name, 'money': 100, 'xp': 0}
    users_db[uid]['xp'] += 1
    users_db[uid]['money'] += 1
    entry = f"[{datetime.now().strftime('%H:%M')}] {message.from_user.first_name}: {message.text}"
    logs.append(entry)

# --- ГЛАВНОЕ МЕНЮ ---
@bot.message_handler(commands=['start'])
def start(message):
    save_log(message)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📂 Новости", "🧬 Мой Персонаж", "💰 Баланс")
    markup.add("🛡 Безопасность", "🏆 Топ", "🎲 Удача")
    bot.send_message(message.chat.id, "🤖 ТЕРМИНАЛ PLAYTIME Co.\nСтатус: Соединение установлено.", reply_markup=markup)

# --- ЖИВОЙ ПЕРСОНАЖ (ИМЯ + ХАРАКТЕР + ЭМОЦИИ) ---
@bot.message_handler(func=lambda message: message.text == "🧬 Мой Персонаж")
def my_char(message):
    save_log(message)
    msg = bot.send_message(message.chat.id, "🧬 Введите ИМЯ для вашего ИИ-персонажа:")
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    save_log(message)
    name = message.text
    user_chars[message.from_user.id] = {'name': name}
    msg = bot.send_message(message.chat.id, f"Принято. Каков ХАРАКТЕР у {name}? (злой, добрый, обидчивый, саркастичный):")
    bot.register_next_step_handler(msg, process_trait)

def process_trait(message):
    save_log(message)
    trait = message.text.lower()
    user_chars[message.from_user.id]['trait'] = trait
    bot.reply_to(message, f"✅ Личность сформирована. {user_chars[message.from_user.id]['name']} теперь в сети. Используйте /hi")

@bot.message_handler(commands=['hi'])
def talk(message):
    save_log(message)
    uid = message.from_user.id
    if uid in user_chars and 'trait' in user_chars[uid]:
        char = user_chars[uid]
        t = char['trait']
        n = char['name']
        
        if "злой" in t:
            ans = ["Свали отсюда.", "Что тебе опять нужно?", "Не беси меня.", "Занят."]
        elif "обидчивый" in t:
            ans = ["Я не хочу с тобой говорить...", "Ты меня расстроил.", "Отстань.", "Молчу."]
        elif "добрый" in t:
            ans = ["Привет! Рад тебя видеть!", "Как дела?", "Я скучал!", "Нужна помощь?"]
        else:
            ans = ["Связь установлена.", "Слушаю.", "Протоколы в норме.", "Ожидаю."]
            
        bot.send_message(message.chat.id, f"📡 [{n}]: {random.choice(ans)}")
    else:
        bot.send_message(message.chat.id, "⚠️ Сначала создай персонажа кнопкой 🧬")

# --- СТАРЫЕ ФУНКЦИИ ---
@bot.message_handler(func=lambda message: message.text == "💰 Баланс")
def balance(message):
    u = users_db[message.from_user.id]
    bot.reply_to(message, f"💳 Кредиты: {u['money']} | XP: {u['xp']}")

@bot.message_handler(func=lambda message: message.text == "📂 Новости")
def news(message):
    bot.send_message(message.chat.id, "📢 НОВОСТИ: Система эмоций обновлена до v.2.0. Стабильность повышена.")

# --- АДМИНКА (4545) ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin(message):
    if message.from_user.id not in verified_admins: verified_admins.append(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Логи чата", "💰 Получить 100к", "🧹 Очистить")
    bot.reply_to(message, "🔓 ДОСТУП РАЗРЕШЕН, ТРОФИМ.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📝 Логи чата")
def show_logs(message):
    if message.from_user.id in verified_admins:
        bot.send_message(message.chat.id, "📡 ПЕРЕХВАТ:\n" + "\n".join(logs[-10:]))

@bot.message_handler(func=lambda message: message.text == "💰 Получить 100к")
def cheat(message):
    if message.from_user.id in verified_admins:
        users_db[message.from_user.id]['money'] += 100000
        bot.reply_to(message, "💵 Баланс пополнен.")

# --- МОНИТОРИНГ ---
@bot.message_handler(func=lambda message: True)
def monitor(message): save_log(message)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
