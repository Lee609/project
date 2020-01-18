import sqlite3


conn = sqlite3.connect('data.db')
cursor = conn.cursor()
cursor.execute('select * from user')
values = cursor.fetchall()
print(values)
