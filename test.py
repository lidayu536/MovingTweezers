import threading
import time



def thread_function(name):
    i = 0
    while True:
        print(f"\r{i}", end='')
        i += 1
        time.sleep(.5)


thread_function("a")