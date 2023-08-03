import sqlite3
from sqlite3 import Error
from datetime import datetime

# Функция для создания подключения к базе данных SQLite3
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

# Функция для выполнения SQL-запросов
def execute_query(conn, query):
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
    except Error as e:
        print(e)

# Функция для создания таблицы, если ее нет
def create_table(conn):
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS finances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        comment TEXT,
        type TEXT,
        date TEXT
    );
    '''
    execute_query(conn, create_table_query)

# Функция для сохранения записи о расходе
def save_expense(user_id, text):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M:%S")
    conn = create_connection("finances.db")
    create_table(conn)
    try:
        # Разделим сообщение на сумму и комментарий
        amount, comment = text.split(' ', 1)
        amount = float(amount)

        # Сохраняем трату в базе данных
        insert_query = f'''
        INSERT INTO finances (user_id, amount, comment, type, date)
        VALUES ({user_id}, {amount}, "{comment}", "expense", "{date}");
        '''
        execute_query(conn, insert_query)

    except ValueError:
        print("Неверный формат траты. Используйте 'СУММА КОММЕНТАРИЙ'")
    finally:
        conn.close()

# Функция для сохранения записи о прибыли
def save_income(user_id, amount):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M:%S")
    conn = create_connection("finances.db")
    create_table(conn)
    try:
        amount = float(amount)

        # Сохраняем прибыль в базе данных
        insert_query = f'''
        INSERT INTO finances (user_id, amount, comment, type, date)
        VALUES ({user_id}, {amount}, "Прибыль", "income", "{date}");
        '''
        execute_query(conn, insert_query)

    except ValueError:
        print("Неверный формат суммы прибыли. Пожалуйста, используйте числовое значение.")
    finally:
        conn.close()

# Функция для получения чистой прибыли
def get_total(user_id):
    conn = create_connection("finances.db")
    query_income = f'''
    SELECT SUM(amount) FROM finances WHERE user_id={user_id} AND type="income";
    '''
    query_expense = f'''
    SELECT SUM(amount) FROM finances WHERE user_id={user_id} AND type="expense";
    '''
    try:
        cursor = conn.cursor()
        cursor.execute(query_income)
        income = cursor.fetchone()[0] or 0

        cursor.execute(query_expense)
        expense = cursor.fetchone()[0] or 0

        total = income - expense
        return total
    except sqlite3.Error as e:
        print(e)
    finally:
        conn.close()

# Функция для получения итога за каждый месяц
def get_monthly_summary(bot, message, user_id, conn):
    cursor = conn.cursor()

    # Выполняем запрос для получения итогов за каждый месяц
    monthly_query = f'''
    SELECT strftime('%Y-%m', date) AS month,
           SUM(CASE WHEN type='income' THEN amount ELSE 0 END) AS total_income,
           SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS total_expense,
           SUM(CASE WHEN type='income' THEN amount ELSE 0 END) - SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS net_income
    FROM finances
    WHERE user_id={user_id}
    GROUP BY strftime('%Y-%m', date);
    '''

    cursor.execute(monthly_query)
    monthly_summary = cursor.fetchall()

    # Форматируем результаты и отправляем пользователю
    summary_text = "Итог за каждый месяц:\n"
    for month, income, expense, net_income in monthly_summary:
        summary_text += f"{month}: Прибыль: {income} рублей, Расход: {expense} рублей, Чистая прибыль: {net_income} рублей\n"

    bot.send_message(message.chat.id, summary_text)

    conn.close()
