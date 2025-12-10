import argparse

class FooAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        if len(values) > 2:
            parser.error(f"{option_string} requires at least 1 but no more than 2 arguments")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-b', '--begin')
    group.add_argument('-d', '--description')
    group.add_argument('-e', '--end', action='store_true')
    group.add_argument('-p', '--pause', action='store_true')
    group.add_argument('-t', '--test', nargs='+', action=FooAction)
    args = parser.parse_args()
    #print(args)
