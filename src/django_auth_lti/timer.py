import time

class Timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print('elapsed time: %f ms' % self.msecs)

'''
Example usage:

from timer import Timer

with Timer() as t:
    do_something()
print "=> elasped lpush: %s s" % t.secs

with Timer as t:
    do_something_else()
print "=> elasped lpop: %s s" % t.secs

'''