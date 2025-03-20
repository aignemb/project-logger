# PROJECT LOGGER

Simple command line interface tool to track and log time spent working on projects.  

## Features
- Track and log time spent working on a project
- Start, stop, pause, resume, cancel, and check the status of tool (idle, running, paused)
- Automatically logs date, time elapsed, and project description to file project_log.csv

## Usage
- Requires python3
- Before running, ensure you are in the **Project Logger** directory (see Optional Setup for alternative)

Usage: python3 project_logger.py [FLAG]... [ARGUMENT]...  
Run help (see exaple below) for detailed usage instructions  

Example to display help menu  
`$ project_logger.py -h`  

## Install
- Requires git

`$ git clone https://github.com/aignemb/project-logger.git`

## Optional Setup
### Aliasing (recommended)
Add the following line to shell configuration file e.g. .bashrc or .zshrc  
alias \<tool alias>="python3 project_logger.py"  
alais \<go to tool alias>="cd \<path/to/tool/folder>; \<tool alais>" (run tool from any directory)

Example:  
`alias pl="python3 project_logger.py"`  
`alias gpl="cd ~/project_logger; pl"`  

With this setup, you can also pass a flag when calling from any directory  
Example:  
`$ gpl -b "project1"`

## Compatibility
Currently only tested on Linux but should work on other OS as well.  

## Coming Soon
- Change name of log file
- Clear log file
- Same project consolodation within given day
