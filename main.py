import telebot
import time
import random
from threading import Thread
from flask import Flask
from datetime import datetime

TOKEN = '8528956901:AAErBMx_VE5QpsOo6Sv_APS26zWzVCeNwys'
bot = telebot.TeleBot(TOKEN)
ADMIN_PASSWORD = "4545"

verified_admins = []
logs = []
user_styles = {} 
last_msg_time = {}
sent_messages = {}
auto_delete_mode = {}

BAD_WORDS = ["мат1", "порно", "18+", "хентай"]

app = Flask('')
@app.route('/')
def home(): return "ANIMATION_MAX_V27"

def run(): app.run(host="0.0.0.0", port=8080)

def check_safety(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    text = message.text.lower() if message.text else ""
    now = time.time()
    if uid in last_msg_time and now - last_msg_time[uid] < 0.6:
        try: bot.delete_message(chat_id, message.message_id)
        except: pass
        return False
    last_msg_time[uid] = now
    if any(word in text for word in BAD_WORDS):
        try: bot.delete_message(chat_id, message.message_id)
        except: pass
        return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    if not check_safety(message): return
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎬 Выбрать Анимацию")
    markup.add("🛡 Безопасность", "🛠 Режим разработчика")
    markup.add("🧹 Удалить мои сообщения", "❌ Сбросить всё")
    bot.send_message(message.chat.id, "💻 **ТЕРМИНАЛ v.27.0: АНИМАЦИОННЫЙ ЦЕНТР**\nВсе системы защиты сохранены.", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🎬 Выбрать Анимацию")
def anim_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📡 Сигнал", "💾 Загрузка", "⌨️ Печать", "🔍 Радар", "🔓 Взлом")
    markup.add("📟 Матрица", "🧪 Вирус", "🧬 Квант", "🔗 Поток", "💻 Код")
    markup.add("🛰 Орбита", "🌊 Волна", "💥 Коллапс", "⚛️ Ядро", "🔄 Синхрон")
    markup.add("🔙 Назад")
    bot.send_message(message.chat.id, "Выберите уникальный режим анимации данных:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🛠 Режим разработчика")
def dev_mode_request(message):
    bot.send_message(message.chat.id, "🔐 Введите ключ доступа:")

@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin_login(message):
    if message.from_user.id not in verified_admins: verified_admins.append(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Логи", "📊 Статус", "🔙 Назад")
    bot.reply_to(message, "🔓 ДОСТУП В ЯДРО ОТКРЫТ.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🛡 Безопасность")
def sec_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⏱ Таймер: 30с (ВКЛ)", "⏱ Таймер (ВЫКЛ)", "🔙 Назад")
    bot.send_message(message.chat.id, "🛡 **ЗАЩИТА**", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    text = message.text
    
    # Список для игнорирования команд
    anim_list = ["📡 Сигнал", "💾 Загрузка", "⌨️ Печать", "🔍 Радар", "🔓 Взлом", 
                 "📟 Матрица", "🧪 Вирус", "🧬 Квант", "🔗 Поток", "💻 Код",
                 "🛰 Орбита", "🌊 Волна", "💥 Коллапс", "⚛️ Ядро", "🔄 Синхрон"]
    
    sys_btns = ["🎬 Выбрать Анимацию", "🛡 Безопасность", "🛠 Режим разработчика", "🔙 Назад", 
                "❌ Сбросить всё", "🧹 Удалить мои сообщения", "📝 Логи", "📊 Статус",
                "⏱ Таймер: 30с (ВКЛ)", "⏱ Таймер (ВЫКЛ)"] + anim_list

    if text in sys_btns:
        if text == "🔙 Назад": start(message)
        elif text == "❌ Сбросить всё":
            user_styles.pop(uid, None)
            bot.send_message(chat_id, "✅ Настройки сброшены.")
        elif text == "⏱ Таймер: 30с (ВКЛ)": auto_delete_mode[uid] = True
        elif text == "⏱ Таймер (ВЫКЛ)": auto_delete_mode[uid] = False
        elif text == "🧹 Удалить мои сообщения":
            if uid in sent_messages:
                for mid in sent_messages[uid]:
                    try: bot.delete_message(chat_id, mid)
                    except: pass
                sent_messages[uid] = []
        elif text in anim_list:
            user_styles[uid] = text
            bot.send_message(chat_id, f"✅ Режим '{text}' активирован.")
        elif text == "📝 Логи" and uid in verified_admins:
            bot.send_message(chat_id, "📡 ЛОГИ:\n" + "\n".join(logs[-10:]))
        return

    if not check_safety(message): return
    logs.append(f"[{datetime.now().strftime('%H:%M')}] {message.from_user.first_name}: {text}")

    if uid in user_styles:
        mode = user_styles[uid]
        try: bot.delete_message(chat_id, message.message_id)
        except: pass
        
        user_name = message.from_user.first_name
        
        # БИБЛИОТЕКА АНИМАЦИЙ
        anims = {
            "📡 Сигнал": ("📡", [".", "..", "...", "📶", "DONE"]),
            "💾 Загрузка": ("💾", ["▯▯▯", "▮▯▯", "▮▮▯", "▮▮▮"]),
            "⌨️ Печать": ("⌨️", ["|", "_", "√", "OK"]),
            "🔍 Радар": ("🔍", ["◦", "◦ ◦", "◦ ◦ ◦", "●"]),
            "🔓 Взлом": ("🔓", ["####", "25%", "60%", "99%", "ACCESS"]),
            "📟 Матрица": ("📟", ["0", "01", "010", "101"]),
            "🧪 Вирус": ("🧪", ["☣️", "☣️☣️", "☣️☣️☣️", "INFECTED"]),
            "🧬 Квант": ("🧬", ["α", "β", "γ", "δ"]),
            "🔗 Поток": ("🔗", ["»", "»»", "»»»", "READY"]),
            "💻 Код": ("💻", ["{ }", "{ ; }", "{ : ; }"]),
            "🛰 Орбита": ("🛰", ["○", "◔", "◑", "◕", "●"]),
            "🌊 Волна": ("🌊", ["~", "~~", "~~~"]),
            "💥 Коллапс": ("💥", ["*", "•", " "]),
            "⚛️ Ядро": ("⚛️", ["◌", "◍", "⦿"]),
            "🔄 Синхрон": ("🔄", ["⬅️", "⬆️", "➡️", "⬇️"])
        }

        if mode in anims:
            icon, frames = anims[mode]
            m = bot.send_message(chat_id, f"{icon} {user_name}: {mode}...")
            if uid not in sent_messages: sent_messages[uid] = []
            sent_messages[uid].append(m.message_id)
            
            for f in frames:
                time.sleep(0.4)
                try: bot.edit_message_text(f"{icon} {user_name}: {f}", chat_id, m.message_id)
                except: break
            
            time.sleep(0.2)
            bot.edit_message_text(f"{icon} {user_name}: {text}", chat_id, m.message_id)
            
            if auto_delete_mode.get(uid):
                def delayed_delete(c_id, m_id):
                    time.sleep(30)
                    try: bot.delete_message(c_id, m_id)
                    except: pass
                Thread(target=delayed_delete, args=(chat_id, m.message_id)).start()

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
