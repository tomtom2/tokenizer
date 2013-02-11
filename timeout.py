#!/usr/bin/env python
# -*- coding: utf8 -*-


from functools import wraps
import errno
import os
import signal
import time

class TimeoutError(Exception):
    pass

def timeout(seconds=120, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            print "timeout!\n"
            return ""
            

        def wrapper(depeche):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            line = ""
            try:
                line = func(depeche)
                print "success!\n"
            except:
                print "an error occured..."
                pass
            finally:
                signal.alarm(0)
            return line

        return wraps(func)(wrapper)

    return decorator

if __name__=='__main__':
    @timeout(3)
    def long_func(nb):
        time.sleep(10)
    
    for i in range(4):
        print "start"
        long_func(5-i-1)
        print "end"
    print "FIN"