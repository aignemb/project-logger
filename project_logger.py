# Project Logger
# command line tool for logging time working on projects

# FLAGS
# -h    help
# -b    begin
# -e    end
# -p    pause
# -s    status
# -r    resume a new timer of the last project used

# TODO: add functionality to handle project description seperately from number

import sys
import json
import datetime
import codecs

now = datetime.datetime.now()

proj_num = ""
date = str(now.month) + "/" + str(now.day)
# time format: [[start1(m), end1(m)], [start2(m), start2(m)]...]
time = []
time_elapsed = 0
state = 0  # 0-idle; 1-running; 2-paused

ui = " Project Logger\n"
db_filename = "pl_db.txt"
log_filename = "project_log.csv"

# load database
with open('pl_db.txt', 'r+', encoding="utf-8") as f:
    db_json = f.read()
    db = json.loads(db_json)

# load documentation
with open('docs.txt', 'r+', encoding="utf-8") as f:
    docs = f.read()


def parse_db():
    global proj_num, time, state, db
    for e in db:
        match e[0]:
            case "project number":
                proj_num = e[1]
            case "time":
                time = e[1]
            case "state":
                state = e[1]


def fill_db():
    global proj_num, time, state, db
    for e in db:
        match e[0]:
            case "project number":
                e[1] = proj_num
            case "time":
                e[1] = time
            case "state":
                e[1] = state


def save_db():
    global db
    fill_db()
    open(db_filename, 'w').close()  # clear the file
    with open(db_filename, 'r+', encoding="utf-8") as f:
        json.dump(db, f)


def flush_db():
    global proj_num, time, state
    time = [[-1, 0]]
    state = 0
    save_db()  # should I have this here or just once at the end of the main function?


def calc_elapsed():
    global time
    minutes = 0
    if len(time) != 0:
        for pair in time:
            minutes += pair[1] - pair[0]
    hours = int(minutes/60)
    minutes = minutes % 60
    return str(hours) + ":" + str(minutes)

def decode_time():
    global time
    log = ""
    for e in time:
        start_minutes = int(e[0] % 60)
        start_hours = int((e[0] - start_minutes) / 60)
        end_minutes = int(e[1] % 60)
        end_hours = int((e[1] - end_minutes) / 60)
        log = log + str(start_hours) + ":" + str(start_minutes) + " - " + str(end_hours) + ":" + str(end_minutes) + ","
    return log


def compose_log():
    global proj_num, time_elapsed
    return date + "," + calc_elapsed() + "," + proj_num + "," + decode_time() + "\n"


def project_logger():
    global proj_num, time, state, db
    argv = sys.argv[1:]  # read in script arguments
    parse_db()
    print(ui)

    if len(argv) > 4:
        print(" error: too many arguments\n for help use -h")
    else:
        if len(argv) == 0:
            argv.append("-s")
        match argv[0]:
            case "-h":  # begin
                print(docs)
            case "-b":  # begin
                if state != 0:
                    print(" error: timer already started, use -s to check state")
                elif len(argv) > 2:
                    print(
                        " error: incorrect number of arguments\n usage: project_logger.py -b <project number [XXXXX]>")
                else:
                    if len(argv) == 1:
                        counter = 0
                        while counter < 3:
                            opt = input(
                                " would you like to continue working on project " + proj_num + "? (y/n): ")
                            print(codecs.escape_decode(
                                bytes("\u001b[1A\u001b[0K", "utf-8"))[0].decode("utf-8"), end="")
                            if opt == 'y':
                                break
                            elif opt == 'n':
                                proj_num = input(
                                    " please enter new project number: ")
                                print(codecs.escape_decode(
                                    bytes("\u001b[1A\u001b[0K", "utf-8"))[0].decode("utf-8"), end="")
                                break
                            counter += 1
                        if counter >= 3:
                            print(" too many failed attempts, quitting...")
                            sys.exit()
                    else:
                        proj_num = argv[1]
                    temp_time = now.hour * 60 + now.minute
                    time = [[temp_time, temp_time]]
                    time_elapsed = calc_elapsed()
                    print(" project number: " + proj_num)
                    print(" elapsed time:   " + time_elapsed)
                    print("\n timer started\n use -p to pause or -e to end")
                    state = 1
                    save_db()
            case "-e":  # end
                if len(argv) != 1:
                    print(
                        " error: incorrect number of arguments\n usage: project_logger.py -e")
                elif state == 0:
                    print(" error: timer not started, use -b to begin")
                elif state == 2:
                    time_elapsed = calc_elapsed()
                    print(" project number: " + proj_num)
                    log = compose_log()
                    print(" elapsed time:   " + time_elapsed)
                    with open(log_filename, 'a', encoding="utf-8") as f:
                        f.write(log)
                    print("\n log saved")
                    flush_db()
                else:
                    time[-1][1] = now.hour * 60 + now.minute
                    time_elapsed = calc_elapsed()
                    print(" project number: " + proj_num)
                    log = compose_log()
                    print(" elapsed time:   " + time_elapsed)
                    with open(log_filename, 'a', encoding="utf-8") as f:
                        f.write(log)
                    print("\n log saved")
                    flush_db()

            case "-p":  # pause
                if len(argv) != 1:
                    print(
                        " error: incorrect number of arguments\n usage: project_logger.py -p")
                elif state != 1:
                    print(" error: timer not running, use -s to check state")
                else:
                    time[-1][1] = now.hour * 60 + now.minute
                    time_elapsed = calc_elapsed()
                    print(" project number: " + proj_num)
                    print(" elapsed time:   " + time_elapsed)
                    print("\n timer paused\n use -r to resume or -e to end")
                    state = 2
                    save_db()
            case "-r":  # resume
                if len(argv) != 1:
                    print(
                        " error: incorrect number of arguments\n usage: project_logger.py -r")
                elif state != 2:
                    print(" error: timer not paused, use -s to check state")
                else:
                    temp_time = now.hour * 60 + now.minute
                    time.append([temp_time, temp_time])
                    time_elapsed = calc_elapsed()
                    print(" project number: " + proj_num)
                    print(" elapsed time:   " + time_elapsed)
                    print("\n timer resumed\n use -p to pause or -e to end")
                    state = 1
                    save_db()
            case "-s":  # status
                if len(argv) != 1:
                    print(
                        " error: incorrect number of arguments\n usage: project_logger.py -s")
                else:
                    if state == 0:
                        time_elapsed = "0:0"
                        message = " timer state:    idle\n\n use -b to begin"
                    elif state == 1:
                        time[-1][1] = now.hour * 60 + now.minute
                        time_elapsed = calc_elapsed()
                        message = " timer state:    running\n\n use -p to pause or -e to end"
                    elif state == 2:
                        time_elapsed = calc_elapsed()
                        message = " timer state:    paused\n\n use -r to resume or -e to end"
                    print(" project number: " + proj_num)
                    print(" elapsed time:   " + time_elapsed)
                    print("\n" + message)
            case "-c":  # cancel
                if len(argv) != 1:
                    print(
                        " error: incorrect number of arguments\n usage: project_logger.py -e")
                elif state == 0:
                    print(" error: timer not started, use -b to begin")
                else:
                    print(" log cancelled")
                    flush_db()


if __name__ == '__main__':
    project_logger()
