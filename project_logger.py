# OUTLINE
# 1. present ui options
# 2a. receive inputs
# 2b. store inputs
# 3. start timer
# 4a. get current time
# 4a. calculate elapsed time
# 4b. present current timer
# 5. present options
# 6. handle pause keystroke
# 7. handle stop keystroke
# 8. when timer is stopped, store date, start time, end time, elapsed time,
# project number

# UI Layout
# Project Time Tracker
# Options: | s - start | s - stop | p - pause | e - exit without saving |
# Project #:    XXXXX
# Start Time:   XX:XX
# Elapsed Time: XX:XX

# NOTES
# o I think I should have the alias as prjt
# o I am going to have it as a true command line interface
#   it will have flags which I will detail
#   pass flags to stop and start and pause etc
# o db has form as below
# [["project number", "XXXXXX"], ...]

# FLAGS
# -h    help
# -b    begin
# -e    end
# -p    pause
# -s    status
# -r    resume a new timer of the last project used

import sys
import json
import datetime

now = datetime.datetime.now()

# load in database
with open('pt_db.txt', 'r+', encoding="utf-8") as f:
    db_json = f.read()
    db = json.loads(db_json)

proj_num = ""
date = str(now.day) + "/" + str(now.month)
# time format: [[start1(m), end1(m)], [start2(m), start2(m)]...]
time = []
time_elapsed = 0
state = 0  # 0-idle; 1-running; 2-paused

ui = " Project Logger\n"


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
    open('pt_db.txt', 'w').close()  # clear the file
    with open('pt_db.txt', 'r+', encoding="utf-8") as f:
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


def compose_log():
    global proj_num, time_elapsed
    return date + "," + calc_elapsed() + "," + proj_num + "\n"


def project_logger():
    global proj_num, time, state, db
    argv = sys.argv[1:]  # read in script arguments
    parse_db()
    print(ui)

    if len(argv) == 0:
        print(" error: too few arguments\n for help use -h")
    else:
        match argv[0]:
            case "-h":  # begin
                print(
                    " -h (help)\n\
 -b (begin)      begin timing a project, requires project number to be passed as second argument\n\
 -e (end)        end timing a project. Appends log of elapsed time to project_log.csv\n\
 -p (pause)      pause timer\n\
 -r (resume)     resume timer\n\
 -s (status)     prints out status of current project timer\n")
            case "-b":  # begin
                # TODO: add functionality to handle project description seperately from number
                # TODO: clear interactive lines after input
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
                                "would you like to continue working on project " + proj_num + "? (y/n): ")
                            if opt == 'y':
                                break
                            elif opt == 'n':
                                proj_num = input(
                                    "please enter new project number: ")
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
                else:
                    time[-1][1] = now.hour * 60 + now.minute
                    time_elapsed = calc_elapsed()
                    print(" project number: " + proj_num)
                    log = compose_log()
                    print(" elapsed time:   " + time_elapsed)
                    with open('project_log.csv', 'a', encoding="utf-8") as f:
                        f.write(log)
                    print("\n log saved")
                    flush_db()

            case "-p":
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
            case "-r":
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
            case "-s":
                if len(argv) != 1:
                    print(
                        " error: incorrect number of arguments\n usage: project_logger.py -s")
                else:
                    if time[0][0] == -1:
                        time_elapsed = "0:0"
                    else:
                        time[-1][1] = now.hour * 60 + now.minute
                        time_elapsed = calc_elapsed()
                    print(" project number: " + proj_num)
                    print(" elapsed time:   " + time_elapsed)
                    if state == 0:
                        print(" timer state:    idle\n\n use -b to begin")
                    elif state == 1:
                        print(
                            " timer state:    running\n\n use -p to pause or -e to end")
                    else:
                        print(
                            " timer state:    paused\n\n use -r to resume or -e to end")
                    save_db()


if __name__ == '__main__':
    project_logger()
