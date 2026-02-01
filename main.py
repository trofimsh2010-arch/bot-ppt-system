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
users_db = {} 
user_chars = {} # {id: {'name': 'Имя', 'trait': 'Характер'}}

app = Flask('')
@app.route('/')
def home(): return "EMOTIONAL SYSTEM ONLINE"

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
    bot.send_message(message.chat.id, "🌋 ТЕРМИНАЛ PLAYTIME Co. (Версия с эмоциями)\nСистемы активны.", reply_markup=markup)

# --- ЛОГИКА ЭМОЦИОНАЛЬНОГО ПЕРСОНАЖА ---
@bot.message_handler(func=lambda message: message.text == "🧬 Мой Персонаж")
def my_char(message):
    save_log(message)
    msg = bot.send_message(message.chat.id, "🧬 Инициализация создания. Сначала введите ИМЯ вашего ИИ:")
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    save_log(message)
    name = message.text
    user_chars[message.from_user.id] = {'name': name}
    msg = bot.send_message(message.chat.id, f"Отлично, его зовут {name}. Теперь опишите его ХАРАКТЕР (например: добрый, злой, обидчивый, дерзкий):")
    bot.register_next_step_handler(msg, process_trait)

def process_trait(message):
    save_log(message)
    trait = message.text.lower()
    user_chars[message.from_user.id]['trait'] = trait
    bot.reply_to(message, f"✅ Протокол завершен. Персонаж {user_chars[message.from_user.id]['name']} с характером '{trait}' готов. Попробуйте /hi")

@bot.message_handler(commands=['hi'])
def talk(message):
    save_log(message)
    user_id = message.from_user.id
    if user_id in user_chars and 'trait' in user_chars[user_id]:
        char = user_chars[user_id]
        trait = char['trait']
        name = char['name']
        
        # Эмоциональные ответы в зависимости от характера
        if "злой" in trait or "дерзкий" in trait:
            responses = ["Чего тебе надо?!", "Не мешай мне работать.", "Отвали, я занят.", "Твои запросы меня бесят."]
        elif "добрый" in trait or "милый" in trait:
            responses = ["Привет, мой создатель! 😊", "Я так рад тебя видеть!", "Чем я могу тебе помочь?", "Ты лучший! ❤️"]
        elif "обидчивый" in trait:
            responses = ["...Я с тобой не разговариваю.", "Ты опять долго не заходил, я обиделся.", "Хм. Оставь меня.", "Я не в настроении."]
        else:
            responses = ["Системы работают.", "Приветствую.", "Ожидаю команд.", "Связь стабильна."]
            
        bot.send_message(message.chat.id, f"📡 [{name}]: {random.choice(responses)}")
    else:
        bot.send_message(message.chat.id, "⚠️ Ошибка: Сначала создайте персонажа через кнопку 🧬")

# --- ОСТАЛЬНЫЕ ФУНКЦИИ ---
@bot.message_handler(func=lambda message: message.text == "💰 Баланс")
def balance(message):
    u = users_db[message.from_user.id]
    bot.reply_to(message, f"💳 Баланс: {u['money']} кред. | XP: {u['xp']}")

@bot.message_handler(func=lambda message: message.text == "📂 Новости")
def news(message):
    bot.send_message(message.chat.id, "📢 НОВОСТИ: Внедрен модуль личностных матриц ИИ.")

# --- РЕЖИМ РАЗРАБОТЧИКА (4545) ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin(message):
    if message.from_user.id not in verified_admins: verified_admins.append(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Логи (Слежка)", "💰 +50к денег", "🧹 Очистить")
    bot.reply_to(message, "🔓 РЕЖИМ АДМИНА АКТИВИРОВАН.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📝 Логи (Слежка)")
def show_logs(message):
    if message.from_user.id in verified_admins:
        bot.send_message(message.chat.id, f"📡 ПЕРЕХВАТ:\n\n" + "\n".join(logs[-15:]))

@bot.message_handler(func=lambda message: message.text == "💰 +50к денег")
def cheat(message):
    if message.from_user.id in verified_admins:
        users_db[message.from_user.id]['money'] += 50000
        bot.reply_to(message, "💵 Успешно.")

# --- ГЛОБАЛЬНАЯ СЛЕЖКА ---
@bot.message_handler(func=lambda message: True)
def monitor(message): save_log(message)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True))
