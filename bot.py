import logging
import telebot
import database

# Уровень логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# Токен вашего бота, полученный от BotFather
TOKEN = "INPUT YOU TOKEN"

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Функция для команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я твой финансовый помощник. Чтобы начать, используй команду /help")

# Функция для команды /help
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,
                     "Привет! Я твой финансовый помощник. Я могу помочь тебе учитывать твои финансы.\n"
                     "Чтобы добавить расход, отправь мне сообщение с суммой и комментарием.\n"
                     "Например: '1000 рублей на обед' или '300 грн такси'.\n"
                     "Чтобы добавить прибыль, используй команду /income.\n"
                     "Чтобы получить чистую прибыль, используй команду /total.\n"
                     "Чтобы получить итог за каждый месяц, используй команду /monthly_summary.")

# Функция для обработки входящих сообщений с тратами
@bot.message_handler(func=lambda message: True and ' ' in message.text and not message.text.startswith('/'))
def record_expense(message):
    user_id = message.from_user.id
    text = message.text
    database.save_expense(user_id, text)
    bot.send_message(message.chat.id, f"Записал расход: {text}")

# Функция для команды /income
@bot.message_handler(commands=['income'])
def record_income(message):
    bot.send_message(message.chat.id, "Введите сумму прибыли:")
    bot.register_next_step_handler(message, process_income_step)

def process_income_step(message):
    user_id = message.from_user.id
    amount = message.text
    database.save_income(user_id, amount)
    bot.send_message(message.chat.id, f"Записал прибыль: {amount}")

# Функция для команды /total
@bot.message_handler(commands=['total'])
def get_total(message):
    user_id = message.from_user.id
    total = database.get_total(user_id)
    bot.send_message(message.chat.id, f"Ваша чистая прибыль: {total} рублей")

# Функция для команды /monthly_summary
@bot.message_handler(commands=['monthly_summary'])
def get_monthly_summary(message):
    user_id = message.from_user.id
    conn = database.create_connection("finances.db")
    database.get_monthly_summary(bot, message, user_id, conn)
    conn.close()

# Запускаем бота
bot.polling()
