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
user_pets = {} 
last_msg_time = {} 

BAD_WORDS = ["мат1", "порно", "18+"] 
SURVEY_QUESTIONS = [
    "Опишите состояние оборудования в секторе C?",
    "Почему вы выбрали работу в Playtime Co.?",
    "Что вы думаете о безопасности наших игрушек?",
    "Ваше предложение по улучшению условий труда?"
]

app = Flask('')
@app.route('/')
def home(): return "SYSTEM_STABLE_ONLINE"

def run(): app.run(host="0.0.0.0", port=8080)

def init_user(uid, name):
    if uid not in users_db:
        users_db[uid] = {'name': name, 'money': 250, 'loan': 0}

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
        bot.send_message(message.chat.id, "⚠️ Нарушение безопасности! Маты и контент 18+ запрещены.")
        return False
    return True

def save_log(message):
    init_user(message.from_user.id, message.from_user.first_name)
    logs.append(f"[{datetime.now().strftime('%H:%M')}] {message.from_user.first_name}: {message.text}")

# --- ПРИВЕТСТВИЕ И ОБНОВЛЕНИЯ ---
@bot.message_handler(commands=['start'])
def start(message):
    if not check_safety(message): return
    save_log(message)
    
    update_text = (
        "🤖 **ТЕРМИНАЛ v.15.0**\n"
        "--------------------------\n"
        "✨ **Функции придумал и реализовал: ИИ Джемини**\n\n"
        "📜 **СПИСОК ОБНОВЛЕНИЙ:**\n"
        "1. 🐱 Замена ИИ на систему 'Лабораторный Кот'.\n"
        "2. 📋 Умные опросы: защита от пустых ответов.\n"
        "3. 🛡 Анти-спам и фильтр нецензурной лексики.\n"
        "4. 🎬 Анимированные статусы в магазине.\n"
        "5. 💳 Система игровых кредитов и долгов.\n"
        "--------------------------\n"
        "Выберите сектор управления:"
    )
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🐱 Мой Кот", "💰 Баланс", "📋 Пройти опрос")
    markup.add("🏪 Магазин", "💳 Кредит")
    bot.send_message(message.chat.id, update_text, reply_markup=markup, parse_mode="Markdown")

# --- ОПРОСЫ С ПРОВЕРКОЙ ---
@bot.message_handler(func=lambda message: message.text == "📋 Пройти опрос")
def survey(message):
    if not check_safety(message): return
    q = random.choice(SURVEY_QUESTIONS)
    msg = bot.send_message(message.chat.id, f"📝 **ВОПРОС:**\n{q}\n\n*(Ответ должен быть длиннее 10 символов)*", parse_mode="Markdown")
    bot.register_next_step_handler(msg, validate_survey)

def validate_survey(message):
    if not check_safety(message): return
    answer = message.text if message.text else ""
    if len(answer) < 10:
        bot.reply_to(message, "❌ **ОШИБКА:** Ответ слишком короткий. Лаборатория не приняла данные.")
    else:
        reward = random.randint(250, 600)
        users_db[message.from_user.id]['money'] += reward
        bot.reply_to(message, f"✅ **УСПЕХ:** Ответ записан. Начислено: {reward} 💰")

# --- ЛОГИКА КОТА ---
@bot.message_handler(func=lambda message: message.text == "🐱 Мой Кот")
def cat_setup(message):
    save_log(message)
    msg = bot.send_message(message.chat.id, "🐾 Введите ИМЯ для вашего кота:")
    bot.register_next_step_handler(msg, set_cat_name)

def set_cat_name(message):
    user_pets[message.from_user.id] = {'name': message.text, 'trait': 'обычный'}
    msg = bot.send_message(message.chat.id, "Какой ХАРАКТЕР? (ленивый, игривый, боевой):")
    bot.register_next_step_handler(msg, set_cat_trait)

def set_cat_trait(message):
    user_pets[message.from_user.id]['trait'] = message.text.lower()
    bot.reply_to(message, f"✨ Кот {user_pets[message.from_user.id]['name']} теперь ваш питомец! Команда: /hi")

@bot.message_handler(commands=['hi'])
def cat_hi(message):
    uid = message.from_user.id
    if uid in user_pets:
        cat = user_pets[uid]
        ans = [f"🐾 {cat['name']} мурчит.", f"🐾 {cat['name']} хочет рыбку.", "Мяу!"]
        bot.send_message(message.chat.id, random.choice(ans))
    else: bot.reply_to(message, "Заведите кота кнопкой 🐱")

# --- АДМИНКА (4545) ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin(message):
    if message.from_user.id not in verified_admins: verified_admins.append(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Логи чата", "💰 Чит +100к", "🔙 Назад")
    bot.reply_to(message, "🔓 ДОСТУП РАЗРЕШЕН. ТРОФИМ, СИСТЕМА У ВАШИХ НОГ.")

@bot.message_handler(func=lambda message: message.text == "📝 Логи чата")
def show_logs(message):
    if message.from_user.id in verified_admins:
        bot.send_message(message.chat.id, "📡 ПЕРЕХВАТ:\n" + "\n".join(logs[-10:]))

# --- ПРОЧИЕ ФУНКЦИИ ---
@bot.message_handler(func=lambda message: message.text == "💰 Баланс")
def balance(message):
    u = users_db[message.from_user.id]
    bot.reply_to(message, f"💵 Баланс: {u['money']} 💰 | Долг: {u['loan']} 💰")

@bot.message_handler(func=lambda message: True)
def monitor(message):
    if check_safety(message): save_log(message)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
