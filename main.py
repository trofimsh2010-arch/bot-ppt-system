import telebot
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
    entry = f"[{datetime.now().strftime('%d.%m %H:%M')}] ID:{message.from_user.id} ({message.from_user.first_name}): {message.text}"
    logs.append(entry)

@bot.message_handler(commands=['start'])
def start(message):
    save_log(message)
    bot.send_message(message.chat.id, "🌋 Система Playtime Co. приветствует вас.\nВведите код доступа.")

@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin_mode(message):
    if message.from_user.id not in verified_admins: verified_admins.append(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📊 Статус", "📝 Логи", "🧹 Очистить")
    bot.reply_to(message, "🔓 ДОСТУП РАЗРЕШЕН.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📝 Логи")
def get_logs_btn(message):
    if message.from_user.id in verified_admins:
        res = "\n".join(logs[-30:]) if logs else "Пусто"
        bot.send_message(message.chat.id, f"📝 ИСТОРИЯ:\n\n{res}")

@bot.message_handler(func=lambda message: True)
def monitor(message): save_log(message)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
