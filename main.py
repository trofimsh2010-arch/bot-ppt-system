import telebot
import time
from threading import Thread
from flask import Flask
from datetime import datetime, timedelta

# --- [1. КОНФИГУРАЦИЯ] ---
TOKEN = '8528956901:AAErBMx_VE5QpsOo6Sv_APS26zWzVCeNwys'
bot = telebot.TeleBot(TOKEN)
ADMIN_PASSWORD = "4545"

verified_admins = [] 
delete_confirmations = set()
failed_attempts = {} 
banned_users = {}

is_destruct_active = False
destruct_finish_time = None
DESTRUCT_DELAY_DAYS = 7 

# --- [2. АВТОНОМНОСТЬ (Flask)] ---
app = Flask('')
@app.route('/')
def home(): return "Protocol 4545: SYSTEM ONLINE"

def run(): app.run(host="0.0.0.0", port=8080)

# --- [3. СИСТЕМА СЛЕЖКИ] ---
def logger(message):
    with open("logs_ppt.txt", "a", encoding="utf-8") as f:
        t = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{t}] {message.from_user.id} | {message.from_user.first_name}: {message.text}\n")

# --- [4. ПРОВЕРКА БЛОКИРОВКИ] ---
def check_ban(user_id):
    if user_id in banned_users:
        if datetime.now() < banned_users[user_id]: return True
        else:
            del banned_users[user_id]
            failed_attempts[user_id] = 0
    return False

# --- [5. ОБРАБОТКА КОМАНД] ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "💀 Система Playtime Co. активна.\n/create — Лаборатория (всем)\nКод 4545 — Управление.")

@bot.message_handler(commands=['create'])
def create(message):
    msg = bot.send_message(message.chat.id, "🧪 Опиши монстра. Я создам фото 1в1.")
    bot.register_next_step_handler(msg, process_lab)

def process_lab(message):
    bot.send_message(message.chat.id, f"⚙️ Генерирую образ монстра для: {message.text}")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if check_ban(message.from_user.id):
        bot.reply_to(message, "🚫 Доступ заблокирован на 7 дней за ошибки кода.")
        return

    logger(message)

    # Фильтр политики
    if any(word in message.text.lower() for word in ['президент', 'война', 'рф', 'украина']):
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "❌ Удалено: Опасность конфиденциальности.")
        return

    # Вход в управление (4545)
    if message.text == ADMIN_PASSWORD:
        if message.from_user.id not in verified_admins:
            verified_admins.append(message.from_user.id)
        failed_attempts[message.from_user.id] = 0
        bot.reply_to(message, "🔓 РЕЖИМ УПРАВЛЕНИЯ.\n/get_logs, /destruct, /cancel_destruct")
        return
    
    # Защита от взлома
    elif message.text.isdigit() and len(message.text) == 4:
        uid = message.from_user.id
        failed_attempts[uid] = failed_attempts.get(uid, 0) + 1
        if failed_attempts[uid] >= 3:
            banned_users[uid] = datetime.now() + timedelta(days=7)
            bot.reply_to(message, "🚨 БАН НА 7 ДНЕЙ.")
        else:
            bot.reply_to(message, f"⚠️ Неверно. Попыток осталось: {3 - failed_attempts[uid]}")

    # Секретные команды управления
    if message.from_user.id in verified_admins:
        if message.text == "/get_logs":
            try:
                with open("logs_ppt.txt", "rb") as f: bot.send_document(message.chat.id, f)
            except: bot.send_message(message.chat.id, "Логи пока пусты.")
        
        # Удаление с отсрочкой в 1 неделю
        if message.text == "/destruct":
            global is_destruct_active, destruct_finish_time
            if is_destruct_active:
                bot.send_message(message.chat.id, f"⏳ В очереди до: {destruct_finish_time}")
                return
            
            delete_confirmations.add(message.from_user.id)
            if len(delete_confirmations) >= 3:
                is_destruct_active = True
                destruct_finish_time = datetime.now() + timedelta(days=DESTRUCT_DELAY_DAYS)
                bot.send_message(message.chat.id, f"🧨 Удаление через 7 дней. Отмена: /cancel_destruct")
            else:
                bot.send_message(message.chat.id, f"⚠️ Ключи: {len(delete_confirmations)}/3")

        if message.text == "/cancel_destruct":
            is_destruct_active = False
            delete_confirmations.clear()
            bot.send_message(message.chat.id, "✅ Удаление отменено.")

if __name__ == "__main__":
    Thread(target=run).start() # Автономность для Render
    bot.polling(none_stop=True)
