import argparse
import sys
import json
import datetime
import codecs

class OneOrTwo(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        if len(values) > 2:
            parser.error(f"{option_string} requires at least 1 but no more than 2 arguments")

# state
# > status
# > current project
# > current task
# > thi
# > days
# > > projects
# > > > tasks



if __name__ == '__main__':

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
        handle_begin(state, args.begin)
    elif args.description != None:
        handle_description(state, args.description)
    elif args.end == True:
        handle_end(state)
    elif args.pause == True:
        handle_pause(state)
    elif args.resume == True:
        handle_resume(state)
    elif args.cancel == True:
        handle_cancel(state)
    elif args.man == True:
        handle_man()
    else: # status or nothing passed
        handle_status(state)
