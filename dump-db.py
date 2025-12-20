import sqlite3

with sqlite3.connect('pl.db') as connection:
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Log;')
    log = cursor.fetchall()

    cursor.execute('SELECT * FROM State;')
    state = cursor.fetchall()

    print('Log')
    for lg in log:
        print(lg)

    print('')

    print('State')
    for st in state:
        print(st)
