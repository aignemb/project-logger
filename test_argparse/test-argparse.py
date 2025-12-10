import argparse

class FooAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        print(len(values))
        if len(values) > 2:
            parser.error(f"{option_string} requires at least 1 but no more than 2 arguments")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=HelpFormatterEXT)
    parser.add_argument('-b', '--begin')
    parser.add_argument('-d', '--description')
    parser.add_argument('-e', '--end', action='store_true')
    parser.add_argument('-p', '--pause', action='store_true')
    parser.add_argument('-t', '--test', nargs='+', action=FooAction)
    args = parser.parse_args()
    #print(args)
