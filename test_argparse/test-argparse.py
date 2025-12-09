import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--begin')
    parser.add_argument('-d', '--description')
    parser.add_argument('-e', '--end', action='store_true')
    parser.add_argument('-p', '--pause', action='store_true')
    args = parser.parse_args()
    print(args)
