from zoe.zs import *

class EchoAgent:
    def __init__(self, host, port, serverhost, serverport):
        self._listener = Listener(host, port, self, serverhost, serverport)

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        tags = parser.tags()
        print ("Echo agent received: " + parser.msg())
        response = self.responseFor(parser)
        self._listener.sendbus(response)

    def responseFor(self, parser):
        aMap = {"src": "echo", "dst": parser.get("src")}
        return MessageBuilder.override(parser, aMap).msg()

