import time
import threading
import configparser
import zoe

class UsersAgent:
    def __init__(self, host, port, serverhost, serverport, interval = 1, conf = "zoe-users.conf"):
        self._listener = zoe.Listener(host, port, self, serverhost, serverport)
        self._model = zoe.Users(conf)
        self._interval = interval
        self.update()

    def update(self):
        self._model.update()
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
            self.notify(parser)

    def notify(self, original = None):
        users = self._model.asmap()
        tags = ["users", "notification"]
        aMap = {"src": "users", "topic": "users", "tag": tags}
        msg = zoe.MessageBuilder(dict(aMap, **users), original).msg()
        self._listener.sendbus(msg)
        
    def loop(self):
        while True:
            time.sleep(self._interval)
            self.update()

