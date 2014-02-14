import sys

def log(env, *args):
    sys.stdout.write('%d' % env.now)
    for string in enumerate(args):
        sys.stdout.write('\t{0}'.format(string[1]))
    sys.stdout.write('\n')
