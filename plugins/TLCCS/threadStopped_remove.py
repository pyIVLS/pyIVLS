# thread stopped by exception for proper finalizing the job without using a stop flag to be checked all the time

import threading
import ctypes


class ThreadStopped(Exception):
    pass


class thread_with_exception(threading.Thread):
    def __init__(self, trgt, *arg):
        threading.Thread.__init__(self, target=trgt, args=arg)

    def get_id(self):
        # returns id of the respective thread
        if hasattr(self, "_thread_id"):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def thread_stop(self):
        thread_id = self.get_id()
        #       res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), ctypes.py_object(SystemExit))
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), ctypes.py_object(ThreadStopped))  # Just not to confuse with any other possible exceptions
        print("trying to stop")
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), 0)
            return [1, "ThreadStopped exception raise failure"]
        print("OK")
        return [0, "ThreadStopped exception sent"]
