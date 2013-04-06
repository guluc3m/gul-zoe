import zoe

class TestAgent:
    def __init__(self, host, port, serverhost, serverport):
        self._listener = zoe.Listener(host, port, self, serverhost, serverport)

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        print ("Test agent received message: " + parser.msg())
        self._parser = parser
        if "dotest" in parser.tags():
            self._listener.sendbus("src=test&dst=echo&str=Hello world!")

agent = TestAgent("localhost", 30101, "localhost", 30000)
agent.start()
