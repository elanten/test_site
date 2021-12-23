import sqlite3

conn = sqlite3.connect('test_data.db')

# Инициализируем базу sqlite выгрузкой из .accdb "как есть"
# Далее работаем только с ней 
with open('init_db.sql', 'r', encoding='utf8') as script:
    curr = conn.cursor()
    curr.executescript(script.read())
    curr.close()
