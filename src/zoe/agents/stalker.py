from zoe.zs import *
import uuid
import sys

class StalkerAgent:
    def __init__(self, host, port, serverhost, serverport, msgparams):
        self._listener = Listener(host, port, self, serverhost, serverport)
        self._source, self._topic, self._original = msgparams
        self._name = "stalker-" + str(uuid.uuid4())
        self._parser = MessageParser(self._original)

    def start(self):
        self._listener.start(self.register)

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        tags = parser.tags()
        source = parser.get("src")
        cid = parser.get("_cid")
        if source == self._source and cid == self._parser.get("_cid"):
            self.unregister()
            self.show(parser)
            self.stop()
            sys.exit(0)
        if "register" in tags and "success" in tags:
            self._listener.sendbus(self._original)

    def register(self):
        self._host = self._listener._host
        self._port = self._listener._port
        aMap = {"dst":"server", "tag":"register", "name":self._name, "host":self._host, "port":str(self._port), "topic":self._topic}
        self._listener.sendbus(MessageBuilder(aMap).msg())
    
    def unregister(self):
        aMap = {"dst":"server", "tag":"unregister", "name":self._name, "topic":self._topic}
        self._listener.sendbus(MessageBuilder(aMap).msg())

    def show(self, parser):
        keys = list(parser._map.keys())
        keys.sort()
        for key in keys:
            print (key + "=" + str(parser.get(key)))

