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

app = Flask('')
@app.route('/')
def home(): return "SYSTEM_FIXED_ONLINE"

def run(): app.run(host="0.0.0.0", port=8080)

def init_user(uid, name):
    if uid not in users_db:
        users_db[uid] = {'name': name, 'money': 0, 'loan': 0}

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
    
    update_text = (
        "🤖 **ТЕРМИНАЛ v.16.0**\n"
        "--------------------------\n"
        "✨ **Функции придумал и реализовал: ИИ Джемини**\n\n"
        "📜 **ОБНОВЛЕНИЯ:**\n"
        "- Опросы удалены. Деньги выдает только админ.\n"
        "- Возвращен ИИ-питомец с выбором характера.\n"
        "- Питомец больше не знает, кто его создал.\n"
        "--------------------------"
    )
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🧬 Мой Питомец", "💰 Баланс")
    markup.add("🏪 Магазин", "💳 Кредит")
    bot.send_message(message.chat.id, update_text, reply_markup=markup, parse_mode="Markdown")

# --- СОЗДАНИЕ ПИТОМЦА ---
@bot.message_handler(func=lambda message: message.text == "🧬 Мой Питомец")
def pet_init(message):
    save_log(message)
    msg = bot.send_message(message.chat.id, "🧬 Введите ИМЯ для вашего ИИ-питомца:")
    bot.register_next_step_handler(msg, set_pet_name)

def set_pet_name(message):
    user_chars[message.from_user.id] = {'name': message.text}
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("1. Ленивый", "2. Игривый", "3. Простой")
    msg = bot.send_message(message.chat.id, f"Выберите характер для {message.text}:", reply_markup=markup)
    bot.register_next_step_handler(msg, set_pet_trait)

def set_pet_trait(message):
    trait = message.text
    user_chars[message.from_user.id]['trait'] = trait
    bot.send_message(message.chat.id, f"✅ Питомец {user_chars[message.from_user.id]['name']} готов! Используй /hi для общения.", reply_markup=telebot.types.ReplyKeyboardRemove())
    # Возвращаем меню после выбора
    start(message)

# --- ОБЩЕНИЕ С ИИ ---
@bot.message_handler(commands=['hi'])
@bot.message_handler(func=lambda message: message.text and message.text.lower().startswith('hi'))
def pet_talk(message):
    save_log(message)
    uid = message.from_user.id
    if uid in user_chars:
        char = user_chars[uid]
        name = char['name']
        trait = char['trait']
        text = message.text.lower()

        # Защита на вопросы о создании
        if "кто тебя создал" in text or "кто твой создатель" in text or "когда ты создан" in text:
            ans = "Не знаю."
        else:
            if "1." in trait: # Ленивый
                ans = random.choice(["А? Что?.. Я сплю.", "Давай потом...", "М-м-м, привет наверное."])
            elif "2." in trait: # Игривый
                ans = random.choice(["О! Привет! Поиграем?", "Я так рад тебя видеть!", "Ура, ты тут!"])
            else: # Простой
                ans = random.choice(["Приветствую.", "На связи.", "Я тут, слушаю тебя."])
        
        bot.send_message(message.chat.id, f"📡 [{name}]: {ans}")
    else:
        bot.reply_to(message, "⚠️ Сначала создай питомца кнопкой 🧬")

# --- АДМИНКА (4545) ---
@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin(message):
    if message.from_user.id not in verified_admins: verified_admins.append(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Логи чата", "💰 Выдать деньги", "🔙 Назад")
    bot.reply_to(message, "🔓 ДОСТУП РАЗРЕШЕН. ТРОФИМ, УПРАВЛЯЙ.")

@bot.message_handler(func=lambda message: message.text == "💰 Выдать деньги")
def give_money_start(message):
    if message.from_user.id in verified_admins:
        msg = bot.send_message(message.chat.id, "Введите ID пользователя и сумму (например: 123456 500):")
        bot.register_next_step_handler(msg, give_money_final)

def give_money_final(message):
    try:
        target_id, amount = message.text.split()
        target_id = int(target_id)
        amount = int(amount)
        if target_id not in users_db: init_user(target_id, "User")
        users_db[target_id]['money'] += amount
        bot.send_message(message.chat.id, f"✅ Выдано {amount} кредитов пользователю {target_id}")
    except:
        bot.reply_to(message, "❌ Ошибка формата. Используй: ID СУММА")

@bot.message_handler(func=lambda message: message.text == "📝 Логи чата")
def show_logs(message):
    if message.from_user.id in verified_admins:
        bot.send_message(message.chat.id, "📡 ПЕРЕХВАТ:\n" + "\n".join(logs[-10:]))

# --- БАЛАНС ---
@bot.message_handler(func=lambda message: message.text == "💰 Баланс")
def balance(message):
    u = users_db[message.from_user.id]
    bot.reply_to(message, f"💵 Твой баланс: {u['money']} 💰\n(Деньги выдаются только администрацией)")

@bot.message_handler(func=lambda message: True)
def monitor(message):
    if check_safety(message): save_log(message)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
