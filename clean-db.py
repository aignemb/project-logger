import sqlite3

with sqlite3.connect('pl.db') as connection:
    cursor = connection.cursor()

    cursor.execute('DROP TABLE IF EXISTS Log;')
    cursor.execute('DROP TABLE IF EXISTS State;')

    connection.commit()
