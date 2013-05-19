import unittest
import sys
import os
import threading
import time

sys.path[0:0] = [os.path.join(os.path.dirname(__file__), ".."),]

import zoe


class TestAgent:
    def __init__(self, port):
        self._listener = zoe.Listener(port, self)

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        print ("Test agent received message: " + parser.msg())
        self._parser = parser


class TestMessageServer (unittest.TestCase):

    def setUp(self):
        self._agent = False
        self._server = False
        self._testagent = False

    def tearDown(self):
        if self._agent:
            self._agent.stop()
        if self._server:
            self._server.stop()
        if self._testagent:
            self._testagent.stop()
        time.sleep(1)

    def test_smoke_echo (self):
        # start the bus
        th = threading.Thread(target = self.launch_server)
        th.start()
        
        # start the echo agent
        th = threading.Thread(target = self.launch_echo_agent)
        th.start()

        # start the test agent
        th = threading.Thread(target = self.launch_test_agent)
        th.start()
        
        # give the threads some time to start listening
        time.sleep(1)

        # register test and echo agent
        self._server.registerAgent ("echo", "localhost", 10010)
        self._server.registerAgent ("test", "localhost", 10011)

        # send a message to the bus
        msg = "Hello world!"
        parser = zoe.MessageParser("src=test&dst=echo&str=" + msg)
        self._server.receive (parser)
        time.sleep(1)

        # the agent should receive the message
        parser = self._testagent._parser
        self.assertEqual ("echo", parser.get("src"))
        self.assertEqual ("test", parser.get("dst"))
        self.assertEqual (msg,    parser.get("str"))

    def test_config (self):
        config = """
[agent agent1]
host: host1
port: 1

[agent agent2]
host: host2
port: 2

[agent agent3]
host: host3
port: 3

[topic topic1]
agents: agent1 agent2

[topic topic2]
agents: agent2 agent3
"""
        server = zoe.Server("localhost", 10000, configstr = config)
        self.assertEqual (3, len(server._agents))
        self.assertEqual (("host1", 1), server._agents["agent1"])
        self.assertEqual (("host2", 2), server._agents["agent2"])
        self.assertEqual (("host3", 3), server._agents["agent3"])
        topics = server._dispatchers[1]._topics
        self.assertEqual (2, len(topics))
        self.assertEqual (["agent1", "agent2"], topics["topic1"])
        self.assertEqual (["agent2", "agent3"], topics["topic2"])

    def launch_echo_agent(self):
        self._agent = zoe.EchoAgent("localhost", 10010, "localhost", 10000)
        self._agent.start()

    def launch_test_agent(self):
        self._testagent = TestAgent(10011)
        self._testagent.start()

    def launch_server(self):
        self._server = zoe.Server("localhost", 10000)
        self._server.start()


class TestDispatchers (unittest.TestCase):
    
    def test_none (self):
        server = zoe.Server("localhost", 10000)
        p = zoe.MessageParser("key=value")
        d = server.destinationFor(p)
        self.assertIsNone (d) 

    def test_p2p_1 (self):
        server = zoe.Server("localhost", 10000)
        p = zoe.MessageParser("dst=test")
        d = server.destinationFor(p)
        self.assertEqual ("test", d)
    
    def test_p2mp (self):
        server = zoe.Server("localhost", 10000)
        p = zoe.MessageParser("dst=test1&dst=test2")
        d = server.destinationFor(p)
        self.assertTrue (d.__class__ is list)
        self.assertEqual (d, ["test1", "test2"])

    def test_topic_with_src (self):
        server = zoe.Server("localhost", 10000)
        tp = server._dispatchers[1]
        tp.add ("topic1", "test1", "test2", "test3")
        tp.add ("topic2", "test3", "test4", "test5")
        p = zoe.MessageParser("src=test1&topic=topic1")
        d = server.destinationFor(p)
        self.assertEqual (d, ["test2", "test3"])
    
    def test_topic_without_src (self):
        server = zoe.Server("localhost", 10000)
        tp = server._dispatchers[1]
        tp.add ("topic1", "test1", "test2", "test3")
        tp.add ("topic2", "test3", "test4", "test5")
        p = zoe.MessageParser("topic=topic1")
        d = server.destinationFor(p)
        self.assertEqual (d, ["test1", "test2", "test3"])

    def test_dst_over_topic (self):
        server = zoe.Server("localhost", 10000)
        tp = server._dispatchers[1]
        tp.add ("topic1", "test1", "test2", "test3")
        tp.add ("topic2", "test3", "test4", "test5")
        p = zoe.MessageParser("dst=dest1&topic=topic1")
        d = server.destinationFor(p)
        self.assertEqual (d, "dest1")

if __name__ == "__main__":
    unittest.main()


