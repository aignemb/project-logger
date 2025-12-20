import argparse
import sys
import json
import datetime
import codecs
import sqlite3
from dataclasses import dataclass, astuple

class OneOrTwo(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        if len(values) > 2:
            parser.error(f"{option_string} requires at least 1 but no more than 2 arguments")
@dataclass
class State:
    status: str
    session: str
    date: str
    project: str
    task: str
    start: str

tooltips = {'idle': 'use -b project [task] to start timer',
            'running': 'use -p to pause, -e to end, or -c to cancel session',
            'paused': 'use -r to resume or -c to cancel'
            }

message = None

def display_ui(state, tooltips, caller_message, elapsed):

    ui = f''' Project Logger

 Status:    {state.status}
 Project:   {state.project}
 Task:      {state.task}
 Elapsed:   {elapsed}

 {caller_message}
 {tooltips[state.status]}
    '''
    print(ui)

def find_elapsed(state, connection, cursor):
    pass

def push_log(state, connection, cursor):
    now = datetime.datetime.now()
    end = now.hour * 60 + now.minute

    push_log_query = '''
    INSERT INTO Log (session, date, project, task, start, end)
    VALUES(?,?,?,?,?,?);
    '''

    cursor.execute(push_log_query, (state.session, state.date, state.project, state.task, state.start, end))
    connection.commit()

def push_state(state, connection, cursor):
    insert_push_query = '''
    INSERT INTO State (status, session, date, project, task, start)
    VALUES(?,?,?,?,?,?);
    '''
    update_push_query = '''
    UPDATE State
    SET status = ? , session = ? , date = ? , project = ? , task = ? , start = ?;
    '''
    cursor.execute('SELECT * FROM State;')
    if cursor.fetchone() is None:
        cursor.execute(insert_push_query, astuple(state))
    else:
        cursor.execute(update_push_query, astuple(state))

    connection.commit()

def handle_status(state, connection, cursor):
    print("status")

def handle_begin(state, connection, cursor, begin_args):
    message = 'timer started, use -p to pause or -e to end'
    if state.status != 'idle':
        message = 'timer already running, use -e to end before starting a timer'
    else:
        state.status = 'running'

        now = datetime.datetime.now()
        state.session = now.strftime('%Y%m%d%H%M%S')
        state.date = str(now.month) + "/" + str(now.day)
        state.start = now.hour * 60 + now.minute

        if len(begin_args) == 1:
            state.project = begin_args[0]
            state.task = 'none'
        else:
            state.project = begin_args[0]
            state.task = begin_args[1]


        push_log(state, connection, cursor)
    return message

def handle_task(state, connection, cursor, args):
    print("task")

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
            id  INTEGER PRIMARY KEY AUTOINCREMENT,
            session TEXT,
            date TEXT,
            project TEXT,
            task TEXT,
            start INTEGER,
            end INTEGER
        );
        ''')
        connection.commit()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS State (
            id  INTEGER PRIMARY KEY,
            status TEXT,
            session TEXT,
            date TEXT,
            project TEXT,
            task TEXT,
            start INTEGER
        );
        ''')
        connection.commit()

        cursor.execute('SELECT status, session, date, project, task, start FROM State;')
        try:
            state = State(*cursor.fetchone())
        except TypeError:
            state = State('idle', 'none', '', '', '', '')

        # Set Up Parser
        parser = argparse.ArgumentParser()

        # Set Up Flags
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-s', '--status', action='store_true')
        group.add_argument('-b', '--begin', nargs='+', action=OneOrTwo, 
                           help='1 \u2264 number of arguments \u2264 2')
        group.add_argument('-t', '--task')
        group.add_argument('-e', '--end', action='store_true')
        group.add_argument('-p', '--pause', action='store_true')
        group.add_argument('-r', '--resume', action='store_true')
        group.add_argument('-c', '--cancel', action='store_true')
        group.add_argument('--man', action='store_true', help='show full manual')

        # Parse Arguments
        args = parser.parse_args()

        # Dispatch
        if args.begin != None:
            message = handle_begin(state, connection, cursor, args.begin)
        elif args.task != None:
            handle_task(state, connection, cursor, args.task)
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

        push_state(state, connection, cursor)

    ### Testing ###

    display_ui(state, tooltips, message, '1:15')
