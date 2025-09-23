# thread stopped by exception for proper finalizing the job without using a stop flag to be checked all the time

import ctypes
import threading


class ThreadStopped(Exception):
    """Custom exception to signal that a thread should stop."""

    def __init__(self, message="Thread stopped by user request."):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"ThreadStopped: {self.message}"

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
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), 0)
            return [1, "ThreadStopped exception raise failure"]
        return [0, "ThreadStopped exception sent"]
