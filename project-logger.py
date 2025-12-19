import argparse
import sys
import json
import datetime
import codecs
import sqlite3
from dataclasses import dataclass

class OneOrTwo(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        if len(values) > 2:
            parser.error(f"{option_string} requires at least 1 but no more than 2 arguments")
@dataclass
class State:
    status: str = 'idle'
    session: str = 'none'

# state
# > status
# > current project
# > current task
# > thi
# > days
# > > projects
# > > > tasks

def handle_status(state, connection, cursor):
    print("status")

def handle_begin(state, connection, cursor, args):
    print("begin")

def handle_description(state, connection, cursor, args):
    print("description")

def handle_end(state, connection, cursor):
    print("end")

def handle_pause(state, connection, cursor):
    print("pause")

def handle_resume(state, connection, cursor):
    print("resume")

def handle_cancel(state, connection, cursor):
    print("cancel")

def handle_man():
    print("man")

if __name__ == '__main__':

    with sqlite3.connect('pl.db') as connection:
        cursor = connection.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Log (
            id  INTEGER PRIMARY KEY,
            session TEXT,
            date TEXT,
            project TEXT,
            task TEXT,
            start INTEGER,
            end INTEGER
        );
        ''')
        connection.commit()

        cursor.execute('DROP TABLE IF EXISTS State;')
        connection.commit()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS State (
            id  INTEGER PRIMARY KEY,
            status TEXT,
            session TEXT
        );
        ''')
        connection.commit()

        state = State()

        cursor.execute('SELECT * FROM State;')
        if cursor.fetchone() is None:
            cursor.execute('''INSERT INTO State (status, session) VALUES(?,?);''', (state.status, state.session))
            print('initializing state\n')
        else:
            state.status = cursor.fetchone()
            state.session = cursor.fetchone()

        print(state.status + ' | ' + state.session + '\n')

        # Set Up Parser
        parser = argparse.ArgumentParser()

        # Set Up Flags
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-s', '--status', action='store_true')
        group.add_argument('-b', '--begin', nargs='+', action=OneOrTwo, 
                           help='1 \u2264 number of arguments \u2264 2')
        group.add_argument('-d', '--description')
        group.add_argument('-e', '--end', action='store_true')
        group.add_argument('-p', '--pause', action='store_true')
        group.add_argument('-r', '--resume', action='store_true')
        group.add_argument('-c', '--cancel', action='store_true')
        group.add_argument('--man', action='store_true', help='show full manual')

        # Parse Arguments
        args = parser.parse_args()

        # Dispatch
        if args.begin != None:
            handle_begin(state, connection, cursor, args.begin)
        elif args.description != None:
            handle_description(state, connection, cursor, args.description)
        elif args.end == True:
            handle_end(state, connection, cursor)
        elif args.pause == True:
            handle_pause(state, connection, cursor)
        elif args.resume == True:
            handle_resume(state, connection, cursor)
        elif args.cancel == True:
            handle_cancel(state, connection, cursor)
        elif args.man == True:
            handle_man()
        else: # status or nothing passed
            handle_status(state, connection, cursor)
