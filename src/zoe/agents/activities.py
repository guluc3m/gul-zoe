from zoe import *
import threading

class ActivitiesAgent:
    def __init__(self, host, port, serverhost, serverport):
        self._listener = Listener(host, port, self, serverhost, serverport)
        self._users = None

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        tags = parser.tags()
        if "memo" in tags:
            self.memo()
        if "users" in tags and "notification" in tags:
            self.updateUsers(parser)
        #self._listener.sendbus(response)

    def updateUsers(self, parser):
        presi = parser.get("presi")
        vice = parser.get("vice")
        self._users = {"presi":presi, "vice":vice}

    def requestUsers(self):
        msg = MessageBuilder({"dst":"users","tag":"notify"}).msg()
        self._listener.sendbus(msg)

    def memo(self):
        print ("Checking prerequisites")
        print ("  Checking user list")
        success = True
        if not self._users:
            self.requestUsers()
            success = False
        print ("  Checking accounting")
        # blah
        if not success:
            print ("Prerequisites not met. Please try again")
            return
        print ("OK, I can generate the activity memo. Here it is:")
        print ()
        print ("  GUL activities memo")
        print ("  -------------------")
        print ()
        print ("  People at GUL:")
        print ("  - Our president is " + self._users["presi"])
        print ("  - Our vicepresident is " + self._users["vice"])
        print ("  Here goes some other stuff...")
