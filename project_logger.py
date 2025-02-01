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

db = []
proj_num = ""
date = str(now.day) + "/" + str(now.month)
# time format: [[start1(m), end1(m)], [start2(m), start2(m)]...]
time = []
time_elapsed = []
paused = 0

ui = "Project Logger"

# load in database
with open('pt_db.txt', 'r+', encoding="utf-8") as f:
    db_json = f.read()
    db = json.loads(db_json)


def parse_db():
    global proj_num, date, time, time_elapsed, db
    for e in db:
        match e[0]:
            case "project number":
                proj_num = e[1]
            case "date":
                e[1] = date
            case "time":
                time = e[1]
            case "time elapsed":
                time_elapsed = e[1]


def fill_db():
    global proj_num, date, time, time_elapsed, db
    for e in db:
        match e[0]:
            case "project number":
                e[1] = proj_num
            case "date":
                e[1] = date
            case "time":
                e[1] = time
            case "time elapsed":
                e[1] = time_elapsed


def save_db():
    global db
    fill_db()
    open('pt_db.txt', 'w').close()  # clear the file
    with open('pt_db.txt', 'r+', encoding="utf-8") as f:
        json.dump(db, f)


def flush_db():
    global proj_num, date, time, time_elapsed, db
    time = []
    time_elapsed = []
    save_db()  # should I have this here or just once at the end of the main function?


def calc_elapsed():
    global time, time_elapsed
    minutes = 0
    for pair in time:
        minutes += pair[1] - pair[0]


def compose_log():
    global proj_num, time_elapsed
    return date + "," + time_elapsed + "," + proj_num + "\n"


def project_logger():
    global proj_num, time, time_elapsed, paused
    argv = sys.argv[1:]  # read in script arguments

    match argv[0]:
        case "-h":  # begin
            pass
        case "-b":  # begin
            # TODO: add functionality to handle project description seperately from number
            if len(argv) != 2:  # begin flag and project number
                print(
                    "error: incorrect number of arguments\nusage: project_logger.py -b <project number [XXXXX]>")
            # elif len(argv[1]) != 5:
                # print("error: invalid project number\nusage: project_logger.py -b <project number [XXXXX]>")
            else:
                proj_num = argv[1]
                time = [[now.hour * 60 + now.minute], [0]]
                print(ui)
                print("Project Number: " + proj_num)
                print("Elapsed Time:   " + time_elapsed)
                print("Timer resumed, use -p to pause or -e to end")
                save_db()
        case "-e":  # end
            if len(argv) != 1:
                print(
                    "error: incorrect number of arguments\nusage: project_logger.py -e")
            else:
                time[-1][1] = now.hour * 60 + now.minute
                time_elapsed = calc_elapsed()
                print(ui)
                print("Project Number: " + proj_num)
                print("Elapsed Time:   " + time_elapsed)
                print("Log saved")
                flush_db()

        case "-p":
            if len(argv) != 1:
                print(
                    "error: incorrect number of arguments\nusage: project_logger.py -p")
            else:
                time[-1][1] = now.hour * 60 + now.minute
                time_elapsed = calc_elapsed()
                print(ui)
                print("Project Number: " + proj_num)
                print("Elapsed Time:   " + time_elapsed)
                with open('pt_db.txt', 'a', encoding="utf-8") as f:
                    f.write(compose_log)
                paused = 1
                print("Timer paused, use -r to resume or -e to end")
                save_db()
        case "-r":
            if len(argv) != 1:
                print(
                    "error: incorrect number of arguments\nusage: project_logger.py -r")
            else:
                time.append([[now.hour * 60 + now.minute], [0]])
                time_elapsed = calc_elapsed()
                print(ui)
                print("Project Number: " + proj_num)
                print("Elapsed Time:   " + time_elapsed)
                print("Timer resumed, use -p to pause or -e to end")
                save_db()
        case "-s":
            if len(argv) != 1:
                print(
                    "error: incorrect number of arguments\nusage: project_logger.py -s")
            else:
                time[-1][1] = now.hour * 60 + now.minute
                time_elapsed = calc_elapsed()
                print(ui)
                print("Project Number: " + proj_num)
                print("Elapsed Time:   " + time_elapsed)
                if paused:
                    print("Timer paused, use -r to resume and -e to end")
                else:
                    print("Timer running, use -p to pause and -e to end")
                save_db()


if __name__ == '__main__':
    project_logger()
