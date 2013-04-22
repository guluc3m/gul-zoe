from zoe import *

class BroadcastAgent:
    def __init__(self, host, port, serverhost, serverport):
        self._listener = Listener(host, port, self, serverhost, serverport)
        self._parser = None
        self.requestUsers()

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        tags = parser.tags()
        if "users" in tags and "notification" in tags:
            self.updateUsers(parser)
        if "send" in tags:
            self.send(parser)

    def updateUsers(self, parser):
        self._parser = parser

    def requestUsers(self):
        msg = MessageBuilder({"dst":"users","tag":"notify"}).msg()
        self._listener.sendbus(msg)

    def send(self, parser):
        if not self._parser:
            self.requestUsers()
        msg = parser.get("msg")
        nicks = self._parser.get("group-broadcast-members")
        for nick in nicks:
            preferred = self._parser.get(nick + "-preferred")
            if preferred == "twitter":
                self.tweet(nick, msg)

    def tweet(self, nick, msg):
        account = self._parser.get(nick + "-twitter")
        tags = {"dst":"twitter", "to":account, "msg":msg}
        self._listener.sendbus(MessageBuilder(tags).msg())
