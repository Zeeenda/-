import sqlite3


# создание таблицы CITY для хранения городов пользователей
def create_table():
    conn = sqlite3.connect('testdb2.sqlite')

    cursor = conn.cursor()

    query = 'CREATE TABLE IF NOT EXISTS city(' \
            'id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,' \
            'user_id TEXT NOT NULL,' \
            'city TEXT NOT NULL)'
    cursor.execute(query)
    conn.commit()

    conn.commit()
    conn.close()


# изменение города для пользователя
def city_set(user_id, city):
    conn = sqlite3.connect('testdb2.sqlite')
    cursor = conn.cursor()

    cursor.execute(f'SELECT city FROM city WHERE user_id={user_id}')
    current_city = cursor.fetchone()
    if not current_city:
        sqlite_insert_query = """INSERT INTO city (user_id, city)  VALUES  (?, ?)"""
        cursor.execute(sqlite_insert_query, (user_id, city))
    else:
        sqlite_insert_query = "UPDATE city SET city = ? WHERE user_id = ?"
        cursor.execute(sqlite_insert_query, (city, user_id))

    conn.commit()
    conn.close()


# получаем город пользователя
def city_get(user_id):
    conn = sqlite3.connect('testdb2.sqlite')
    cursor = conn.cursor()

    cursor.execute(f'SELECT city FROM city WHERE user_id={user_id}')
    city = cursor.fetchone()
    conn.close()

    if city:
        return city[0]
    else:
        return None
