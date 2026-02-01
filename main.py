import telebot
import random
from threading import Thread
from flask import Flask
from datetime import datetime

TOKEN = '8528956901:AAErBMx_VE5QpsOo6Sv_APS26zWzVCeNwys'
bot = telebot.TeleBot(TOKEN)
ADMIN_PASSWORD = "4545"

# --- БАЗА ДАННЫХ ---
verified_admins = []
logs = []
users_db = {} # {id: {'name': '', 'money': 100, 'xp': 0}}
user_chars = {} # {id: 'Имя Персонажа'}

app = Flask('')
@app.route('/')
def home(): return "SYSTEM ONLINE"

def run(): app.run(host="0.0.0.0", port=8080)

def init_user(user_id, name):
    if user_id not in users_db:
        users_db[user_id] = {'name': name, 'money': 100, 'xp': 0}

def save_log(message):
    init_user(message.from_user.id, message.from_user.first_name)
    users_db[message.from_user.id]['xp'] += 1
    users_db[message.from_user.id]['money'] += 1
    entry = f"[{datetime.now().strftime('%H:%M')}] {message.from_user.first_name}: {message.text}"
    logs.append(entry)

# --- ГЛАВНОЕ МЕНЮ ---
@bot.message_handler(commands=['start'])
def start(message):
    save_log(message)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📂 Новости", "🧬 Мой Персонаж", "💰 Баланс")
    markup.add("🛡 Безопасность", "🏆 Топ", "🎲 Удача")
    bot.send_message(message.chat.id, f"🌋 ТЕРМИНАЛ PLAYTIME Co.\nСтатус: В сети. Пользователь: {message.from_user.first_name}", reply_markup=markup)

# --- ЛОГИКА ПЕРСОНАЖА (ПРИНЯТИЕ ИМЕНИ) ---
@bot.message_handler(func=lambda message: message.text == "🧬 Мой Персонаж")
def my_char(message):
    save_log(message)
    if message.from_user.id in user_chars:
        bot.send_message(message.chat.id, f"🤖 Ваш текущий ИИ: {user_chars[message.from_user.id]}\nИспользуйте /hi для связи.\n\nХотите изменить имя? Просто введите новое имя прямо сейчас.")
    else:
        bot.send_message(message.chat.id, "🧬 ИИ не обнаружен. Введите ИМЯ для вашего нового персонажа:")
    
    bot.register_next_step_handler(message, set_char_name)

def set_char_name(message):
    save_log(message)
    new_name = message.text
    if len(new_name) > 20:
        bot.reply_to(message, "❌ Имя слишком длинное (макс. 20 символов). Попробуйте еще раз через меню.")
    else:
        user_chars[message.from_user.id] = new_name
        bot.reply_to(message, f"✅ Протокол завершен. Персонаж [{new_name}] зарегистрирован. Напишите /hi")

@bot.message_handler(commands=['hi'])
def talk(message):
    save_log(message)
    if message.from_user.id in user_chars:
        name = user_chars[message.from_user.id]
        bot.send_message(message.chat.id, f"📡 [{name}]: Приветствую, создатель. Системы в норме.")
    else:
        bot.send_message(message.chat.id, "⚠️ Ошибка: Сначала дайте имя персонажу в меню 🧬")

# --- СТАРЫЕ ФУНКЦИИ (ЭКОНОМИКА / НОВОСТИ) ---
@bot.message_handler(func=lambda message: message.text == "💰 Баланс")
def balance(message):
    save_log(message)
    u = users_db[message.from_user.id]
    bot.reply_to(message, f"💳 Баланс: {u['money']} кредитов\n🌟 XP: {u['xp']}")

@bot.message_handler(func=lambda message: message.text == "🎲 Удача")
def roll(message):
    save_log(message)
    cost = 30
    if users_db[message.from_user.id]['money'] >= cost:
        users_db[message.from_user.id]['money'] -= cost
        prize = random.choice([0, 0, 100, 200])
        users_db[message.from_user.id]['money'] += prize
        bot.reply_to(message, f"🎰 Результат: +{prize} 💰 (Затрачено: {cost})")
    else:
        bot.reply_to(message, "❌ Недостаточно кредитов.")

@bot.message_handler(func=lambda message: message.text == "📂 Новости")
def news(message):
    save_log(message)
    bot.send_message(message.chat.id, "📢 НОВОСТИ: Обновлена система именования ИИ. Улучшена защита данных.")

# --- РЕЖИМ РАЗРАБОТЧИКА (4545) ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin(message):
    if message.from_user.id not in verified_admins: verified_admins.append(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Логи (Слежка)", "📊 База", "💰 Сделать богатым", "🧹 Очистить")
    bot.reply_to(message, "🔓 ДОСТУП АДМИНИСТРАТОРА РАЗРЕШЕН.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📝 Логи (Слежка)")
def show_logs(message):
    if message.from_user.id in verified_admins:
        res = "\n".join(logs[-15:]) if logs else "Пусто."
        bot.send_message(message.chat.id, f"📡 ПЕРЕХВАТ СООБЩЕНИЙ:\n\n{res}")

@bot.message_handler(func=lambda message: message.text == "💰 Сделать богатым")
def cheat(message):
    if message.from_user.id in verified_admins:
        users_db[message.from_user.id]['money'] += 50000
        bot.reply_to(message, "💵 Чит-код активирован: +50,000!")

# --- СЛЕЖКА ЗА ВСЕМИ ---
@bot.message_handler(func=lambda message: True)
def monitor(message):
    save_log(message)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
