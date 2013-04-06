import time
import threading
from zoe.zs import *

class UsersAgent:
    def __init__(self, host, port, serverhost, serverport, interval = 1):
        self._listener = Listener(host, port, self, serverhost, serverport)
        self._interval = interval
        self.update()

    def update(self):
        # whatever
        self._users = {"presi": "roberto", "vice": "whoever"}
        self.notify()

    def start(self):
        if (self._interval > 0):
            self._resendDaemonThread = threading.Thread (target = self.loop)
            self._resendDaemonThread.start()
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        tags = parser.tags()
        if "notify" in tags:
            self.notify()

    def notify(self):
        tags = ["users", "notification"]
        aMap = {"src": "users", "topic": "users", "tag": tags}
        msg = MessageBuilder(dict(aMap, **self._users)).msg()
        self._listener.sendbus(msg)
        
    def loop(self):
        while True:
            time.sleep(self._interval)
            self.notify()

