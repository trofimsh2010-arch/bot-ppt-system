import telebot
from threading import Thread
from flask import Flask
from datetime import datetime

TOKEN = '8528956901:AAErBMx_VE5QpsOo6Sv_APS26zWzVCeNwys'
bot = telebot.TeleBot(TOKEN)
ADMIN_PASSWORD = "4545"

verified_admins = []
logs = []
user_chars = {} # База персонажей пользователей

app = Flask('')
@app.route('/')
def home(): return "TERMINAL ONLINE"

def run(): app.run(host="0.0.0.0", port=8080)

def save_log(message):
    entry = f"[{datetime.now().strftime('%H:%M')}] ID:{message.from_user.id} ({message.from_user.first_name}): {message.text}"
    logs.append(entry)

@bot.message_handler(commands=['start'])
def start(message):
    save_log(message)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📂 База данных ИИ", "🛠 Создать/Изменить ИИ")
    bot.send_message(message.chat.id, "🚧 СИСТЕМА PLAYTIME CO. v.4.0\nВведите код доступа или выберите модуль.", reply_markup=markup)

# --- СИСТЕМА ПЕРСОНАЖА ---
@bot.message_handler(func=lambda message: message.text == "🛠 Создать/Изменить ИИ")
def setup_char(message):
    save_log(message)
    msg = bot.send_message(message.chat.id, "📝 Введите имя и тип вашего ИИ (например: 'Хагги, Охранник' или 'Альфа, Робот'):")
    bot.register_next_step_handler(msg, process_char_step)

def process_char_step(message):
    user_chars[message.from_user.id] = message.text
    bot.reply_to(message, f"✅ Объект [{message.text}] успешно зарегистрирован в системе.")

@bot.message_handler(commands=['hi'])
def talk_to_ai(message):
    save_log(message)
    if message.from_user.id in user_chars:
        char_name = user_chars[message.from_user.id]
        bot.send_message(message.chat.id, f"📡 [{char_name}]: Связь установлена. Я слушаю вас, создатель.")
    else:
        bot.send_message(message.chat.id, "⚠️ Ошибка: ИИ не найден. Сначала используйте 'Создать/Изменить ИИ'.")

@bot.message_handler(func=lambda message: message.text == "📂 База данных ИИ")
def db_info(message):
    save_log(message)
    bot.send_message(message.chat.id, "🗄 Список существующих моделей: Хагги, Кисси, Кот-Дремот, Прототип. Вы можете выбрать их или создать свою.")

# --- АДМИНКА (4545) ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin_auth(message):
    if message.from_user.id not in verified_admins: verified_admins.append(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Логи", "📊 Статус", "🧹 Очистить", "🔙 Выход")
    bot.reply_to(message, "🔓 ДОСТУП УРОВНЯ 5 РАЗРЕШЕН.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📝 Логи")
def show_logs(message):
    if message.from_user.id in verified_admins:
        res = "\n".join(logs[-25:]) if logs else "Логов нет."
        bot.send_message(message.chat.id, f"📡 АКТИВНОСТЬ:\n\n{res}")

@bot.message_handler(func=lambda message: message.text == "📊 Статус")
def show_status(message):
    if message.from_user.id in verified_admins:
        bot.send_message(message.chat.id, f"⚙️ СИСТЕМА: СТАБИЛЬНО\n👥 АКТИВНЫХ ИИ: {len(user_chars)}")

# --- СЛЕЖКА ---
@bot.message_handler(func=lambda message: True)
def monitor(message): save_log(message)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
