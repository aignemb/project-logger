#!/usr/bin/bash
PS4='----> '
set -x
python3 clean-db.py
python3 project-logger.py -b 25030 atask
python3 dump-db.py
python3 project-logger.py -b 25030 anothertask
python3 project-logger.py -e
python3 dump-db.py
