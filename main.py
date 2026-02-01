import telebot
import time
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
user_styles = {} 
last_msg_time = {}
sent_messages = {}
auto_delete_mode = {} # {uid: True/False}

BAD_WORDS = ["мат1", "порно", "18+", "хентай"]

app = Flask('')
@app.route('/')
def home(): return "SYSTEM_STABLE_V26"

def run(): app.run(host="0.0.0.0", port=8080)

# --- БЕЗОПАСНОСТЬ ---
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

# --- СТИЛИ ---
def apply_style(text, style):
    if style == "M O N O": return ' '.join(text.upper())
    if style == "Reverse": return text[::-1]
    if style == "Cyber": return f"⚡[01]{text.replace(' ','_')}[10]⚡"
    if style == "Gothic": return f"𝔊𝔬𝔱𝔥𝔦𝔠: {text}"
    if style == "Bubble": return f"Ⓤ {text} Ⓤ"
    if style == "SmallCaps": return text.lower().translate(str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"))
    if style == "Mirror": return f"{text} | {text[::-1]}"
    if style == "Bold": return f"*{text}*"
    if style == "Underline": return f"_{text}_"
    if style == "Strike": return f"~{text}~"
    return text

# --- МЕНЮ ---
@bot.message_handler(commands=['start'])
def start(message):
    if not check_safety(message): return
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎭 Стили текста", "🎬 Анимации")
    markup.add("🛡 Безопасность", "🛠 Режим разработчика")
    markup.add("🧹 Удалить мои сообщения", "❌ Сбросить всё")
    bot.send_message(message.chat.id, "💻 **ЦЕНТРАЛЬНЫЙ ТЕРМИНАЛ v.26.0**\nФункции ИИ Джемини восстановлены.", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🛠 Режим разработчика")
def dev_mode_request(message):
    bot.send_message(message.chat.id, "🔐 Введите секретный ключ доступа:")

@bot.message_handler(func=lambda message: message.text == ADMIN_PASSWORD)
def admin_login(message):
    if message.from_user.id not in verified_admins: verified_admins.append(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Логи", "📊 Статус системы", "🔙 Назад")
    bot.reply_to(message, "🔓 РЕЖИМ РАЗРАБОТЧИКА.\nДоступ к ядру открыт.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📊 Статус системы")
def sys_status(message):
    if message.from_user.id in verified_admins:
        bot.send_message(message.chat.id, f"📡 **STATUS**\nUptime: 100%\nActive Users: {len(user_styles)}\nSafety: High", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🛡 Безопасность")
def sec_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⏱ Таймер: 30с (ВКЛ)", "⏱ Таймер (ВЫКЛ)", "🔙 Назад")
    bot.send_message(message.chat.id, "🛡 **НАСТРОЙКИ ЗАЩИТЫ**\nЗдесь можно включить авто-удаление ваших стилизованных сообщений.", reply_markup=markup)

# --- ОБРАБОТЧИК ---
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    text = message.text
    
    sys_btns = ["🎭 Стили текста", "🎬 Анимации", "🛡 Безопасность", "🧹 Удалить мои сообщения", "🔙 Назад", 
                "❌ Сбросить всё", "🛠 Режим разработчика", "M O N O", "Reverse", "Cyber", "Gothic", 
                "Bubble", "SmallCaps", "Mirror", "Bold", "Underline", "Strike",
                "📡 Передача", "💾 Загрузка", "⌨️ Печать", "🔍 Сканирование", "🔓 Взлом",
                "📝 Логи", "📊 Статус системы", "⏱ Таймер: 30с (ВКЛ)", "⏱ Таймер (ВЫКЛ)"]

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
        elif text in sys_btns[7:17] or text in sys_btns[17:22]:
            user_styles[uid] = text
            bot.send_message(chat_id, f"✅ Установлен режим: {text}")
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
        
        # ВОЗВРАТ ПОЛНОЙ АНИМАЦИИ
        if mode in ["📡 Передача", "💾 Загрузка", "⌨️ Печать", "🔍 Сканирование", "🔓 Взлом"]:
            anim_icons = {"📡 Передача": "📡", "💾 Загрузка": "💾", "⌨️ Печать": "⌨️", "🔍 Сканирование": "🔍", "🔓 Взлом": "🔓"}
            icon = anim_icons[mode]
            m = bot.send_message(chat_id, f"{icon} {user_name}: Инициализация...")
            
            # Сохраняем для удаления
            if uid not in sent_messages: sent_messages[uid] = []
            sent_messages[uid].append(m.message_id)
            
            # Удлиненная анимация
            frames = ["▯▯▯▯", "▮▯▯▯", "▮▮▯▯", "▮▮▮▯", "▮▮▮▮", f"OK: {text}"]
            for f in frames:
                time.sleep(0.5)
                try: bot.edit_message_text(f"{icon} {user_name}: {f}", chat_id, m.message_id)
                except: break
                
            # Авто-удаление через 30с если включено
            if auto_delete_mode.get(uid):
                def delayed_delete(c_id, m_id):
                    time.sleep(30)
                    try: bot.delete_message(c_id, m_id)
                    except: pass
                Thread(target=delayed_delete, args=(chat_id, m.message_id)).start()
        else:
            styled = apply_style(text, mode)
            m = bot.send_message(chat_id, f"👤 {user_name}: {styled}")
            if uid not in sent_messages: sent_messages[uid] = []
            sent_messages[uid].append(m.message_id)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
