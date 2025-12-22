import argparse
import sys
import json
from datetime import datetime, timedelta
import codecs
import sqlite3
from dataclasses import dataclass, astuple

class OneOrTwo(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        if len(values) > 2:
            parser.error(f"{option_string} requires at least 1 but no more than 2 arguments")
@dataclass(slots=True)
class State:
    status: str
    session: str
    project: str
    task: str
    start: str

tooltips = {'idle': 'use -b project [task] to start timer',
            'running': 'use -p to pause, -e to end, or -c to cancel session',
            'paused': 'use -r to resume or -c to cancel'
            }

message = None

def date_to_str(date):
    return date.isoformat(sep=' ', timespec='seconds')

def str_to_date(date_str):
    return datetime.fromisoformat(date_str)

def display_ui(state, tooltips, caller_message, elapsed):

    elapsed_hm = str(elapsed)
    elapsed_hm = elapsed_hm[:4]

    status = state.status
    if status == 'running':
        status = '\033[32mrunning\033[0m'
    elif status == 'paused':
        status = '\033[33mpaused\033[0m'

    ui = f'''\033[1;34m------------------------------------------------------------\033[0m
 \033[1;34mProject Logger\033[0m

 Status:    {status}
 Project:   {state.project}
 Task:      {state.task}
 Elapsed:   {elapsed_hm}

 {caller_message}
 hint: {tooltips[state.status]}
\033[1;34m-----------------------------------------------------------\033[0m
    '''
    print(ui)

def find_elapsed(state, connection, cursor):
    if state.status == 'idle':
        return timedelta(minutes=0)

    now = datetime.now()
    elapsed = now - str_to_date(state.start)

    find_in_session_query = '''
    SELECT start, end FROM Log
    WHERE session = ? AND task = ?;
    '''

    cursor.execute(find_in_session_query, (state.session, state.task))

    log = cursor.fetchone()
    while log is not None:
        elapsed += str_to_date(log[1]) - str_to_date(log[0])
        log = cursor.fetchone()

    if elapsed.days > 0:
        # should make this more elegant
        print(' Total time elapsed: ' + str(elapsed) + '\n')
        raise RuntimeError(f'\033[31mproject-logger does not currently support running for over 24 hours\033[0m')

    return elapsed

def push_log(state, connection, cursor):
    end = date_to_str(datetime.now())

    push_log_query = '''
    INSERT INTO Log (session, project, task, start, end)
    VALUES(?,?,?,?,?);
    '''

    cursor.execute(push_log_query, (state.session, state.project, state.task, state.start, end))
    connection.commit()

def push_state(state, connection, cursor):
    insert_push_query = '''
    INSERT INTO State (status, session, project, task, start)
    VALUES(?,?,?,?,?);
    '''
    update_push_query = '''
    UPDATE State
    SET status = ? , session = ? , project = ? , task = ? , start = ?;
    '''
    cursor.execute('SELECT * FROM State;')
    if cursor.fetchone() is None:
        cursor.execute(insert_push_query, astuple(state))
    else:
        cursor.execute(update_push_query, astuple(state))

    connection.commit()

def handle_status(state, connection, cursor):
    return ''

def handle_begin(state, connection, cursor, begin_args):
    state.status = 'running'
    now = datetime.now()
    state.session = now.strftime('%Y%m%d%H%M%S')
    state.start = date_to_str(now)

    if len(begin_args) == 1:
        state.project = begin_args[0]
        state.task = 'none'
    else:
        state.project = begin_args[0]
        state.task = begin_args[1]

    return 'timer started'

def handle_task(state, connection, cursor, task):
    end = datetime.now()
    start = str_to_date(state.start)

    if end < start:
        # should not happen unless ability to edit start and end datetime is added
        return f'\033[31mERROR: end date after start date\033[0m'

    push_log(state, connection, cursor)
    state.start = date_to_str(end)
    state.task = task
    return 'new task started'

def handle_end(state, connection, cursor):
    end = datetime.now()
    start = str_to_date(state.start)

    if end < start:
        # should not happen unless ability to edit start and end datetime is added
        return f'\033[31mERROR: end date after start date\033[0m'

    push_log(state, connection, cursor)
    state.status = 'idle'
    state.session = '-'
    state.project = '-'
    state.task = '-'
    return 'timer ended, log saved successfully'

def handle_pause(state, connection, cursor):
    end = datetime.now()
    start = str_to_date(state.start)

    if end < start:
        # should not happen unless ability to edit start and end datetime is added
        return f'\033[31mERROR: end date after start date\033[0m'

    state.status = 'paused'
    push_log(state, connection, cursor)
    state.start = date_to_str(end)
    return 'timer paused'

def handle_resume(state, connection, cursor):
    state.status = 'running'
    now = datetime.now()
    state.start = date_to_str(now)
    return 'timer resumed'

def handle_cancel(state, connection, cursor):

    cancel_query = '''
    DELETE FROM Log
    WHERE session = ?
    AND task = ?;
    '''
    cursor.execute(cancel_query, (state.session, state.task))

    state.status = 'idle'
    state.session = '-'
    state.project = '-'
    state.task = '-'

    return 'task cancelled'

def handle_man():
    print("man")

if __name__ == '__main__':

    with sqlite3.connect('pl.db') as connection:
        cursor = connection.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Log (
            id  INTEGER PRIMARY KEY AUTOINCREMENT,
            session TEXT,
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
            project TEXT,
            task TEXT,
            start INTEGER
        );
        ''')
        connection.commit()

        cursor.execute('SELECT status, session, project, task, start FROM State;')
        try:
            state = State(*cursor.fetchone())
        except TypeError:
            state = State('idle', 'none', '', '', '')

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
        group.add_argument('-R', '--report')
        group.add_argument('--man', action='store_true', help='show full manual')

        # Parse Arguments
        args = parser.parse_args()

        # Dispatch
        if args.begin is not None:
            if state.status != 'idle':
                message = f'\033[31mERROR: timer already running\033[0m'
            else:
                message = handle_begin(state, connection, cursor, args.begin)

        elif args.task is not None:
            if state.status == 'idle':
                message = f'\033[31mERROR: timer not running\033[0m'
            else:
                message = handle_task(state, connection, cursor, args.task)

        elif args.end == True:
            if state.status == 'idle':
                message = f'\033[31mERROR: timer not running\033[0m'
            else:
                message = handle_end(state, connection, cursor)

        elif args.pause == True:
            if state.status == 'idle':
                message = f'\033[31mERROR: timer not running\033[0m'
            elif state.status == 'paused':
                message = f'\033[31mERROR: timer already paused\033[0m'
            else:
                message = handle_pause(state, connection, cursor)

        elif args.resume == True:
            if state.status == 'idle':
                message = f'\033[31mERROR: timer not running\033[0m'
            elif state.status == 'running':
                message = f'\033[31mERROR: timer already running\033[0m'
            else:
                message = handle_resume(state, connection, cursor)

        elif args.cancel == True:
            if state.status == 'idle':
                message = f'\033[31mERROR: timer not running\033[0m'
            else:
                message = handle_cancel(state, connection, cursor)

        elif args.man == True:
            handle_man()

        elif args.report is not None:
            if state.status != 'idle':
                ans = input(f'\033[1;34mtimer is still running, are you sure you want to generate raport? (y/n):\033[0m')
                if ans == 'y' or ans == 'yes' or ans == 'Y':
                    pass
                else:
                    print('report cancelled')
                    sys.exit(0)

            sys.exit(0)

        else: # status or nothing passed
            message = handle_status(state, connection, cursor)

        push_state(state, connection, cursor)

    ### Testing ###

    display_ui(state, tooltips, message,find_elapsed(state, connection, cursor))
