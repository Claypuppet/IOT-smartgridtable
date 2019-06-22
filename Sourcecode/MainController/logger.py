from settings import DEBUG

def log(*args):
    if DEBUG:
        for val in args: print val,
        print ''
