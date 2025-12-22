#!/usr/bin/bash
PS4='----> '
set -x
python3 clean-db.py
python3 project-logger.py -b 25030 atask
python3 project-logger.py -b 25030 anothertask
python3 project-logger.py -e
python3 project-logger.py -b 25030 anothertask
python3 project-logger.py -t anothirdtask
python3 project-logger.py -p
python3 dump-db.py
python3 project-logger.py -r
python3 dump-db.py
