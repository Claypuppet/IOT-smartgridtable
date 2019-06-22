import threading
import thread


def start_daemon_thread(func, args=None, start=True):
    th = threading.Thread(target=func, args=args)
    th.daemon = True
    if start:
	    th.start()
    return th

def start_daemon_timer(delay, func, args=None, start=True):
    if not args:
        args = []
    th = threading.Timer(delay, func, args=args)
    th.daemon = True
    if start:
	    th.start()
    return th