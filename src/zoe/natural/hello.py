
import zoe

class HelloCmd:
    def __init__(self, fromdef):
        self._listener = zoe.Listener(None, None, self, "localhost", 30000, True)
        self._fromdef = fromdef

    def execute(self, objects):
        users = objects["users"]
        if self._fromdef is None:
            f = None
            t = users
        else:
            f = users[self._fromdef]
            t = [x for x in users if f != x]

        for u in t:
            if f:
                text = "hello from @" + f["twitter"] + "!"
            else:
                text = "hello!"
            params = {"dst":"twitter", "to":u["twitter"], "msg":text}
            msg = zoe.MessageBuilder(params).msg()
            self._listener.sendbus(msg)

