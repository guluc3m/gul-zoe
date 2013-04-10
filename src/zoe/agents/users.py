import time
import threading
import configparser
from zoe.zs import *

class UsersAgent:
    def __init__(self, host, port, serverhost, serverport, interval = 1, conf = "zoe-users.conf"):
        self._listener = Listener(host, port, self, serverhost, serverport)
        self._interval = interval
        self._config = configparser.ConfigParser()
        self._config.read(conf)
        self.update()

    def update(self):
        users = {}
        for section in self._config.sections():
            kind, name = section.split(" ")
            if kind == "group":
                for key in self._config[section]:
                    users["group-" + name + "-" + key] = self._config[section][key]
            else:
                for key in self._config[section]:
                    users[name + "-" + key] = self._config[section][key]
        self._users = users
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
            self.update()

