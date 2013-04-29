# -*- coding: utf-8 -*-
#
# This file is part of Zoe Assistant - https://github.com/guluc3m/gul-zoe
#
# Copyright (c) 2013 David Muñoz Díaz <david@gul.es> 
#
# This file is distributed under the MIT LICENSE
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import socket
import threading
import configparser
import time
from zoe.zp import *
from zoe.listener import *
from zoe.ptp import *
from zoe.topic import *

class Server:
    def __init__(self,                         \
                 host = "localhost",           \
                 port = 30000,                 \
                 configstr = None,             \
                 configfile = None,            \
                 debug = True):
        self._dispatchers = []
        self._agents = {}
        self._agentslookup = {}
        self._listener = Listener(host, port, self, host, port)
        self._config = configparser.ConfigParser()
        if configfile:
            self._config.read(configfile)
        if configstr:
            self._config.read_string(configstr)
        self.registerAgents()
        self._ptpdispatcher = PTPDispatcher(self._config)
        self._topicdispatcher = TopicDispatcher(self._config)
        self.registerDispatcher(self._ptpdispatcher)
        self.registerDispatcher(self._topicdispatcher)
        self._debug = debug

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def registerAgents(self):
        for section in self._config.sections():
            sectype, secname = section.split(" ")
            if sectype == "agent":
                host = self._config[section]["host"]
                port = int(self._config[section]["port"])
                self.registerAgent (secname, host, port)

    def registerDispatcher(self, dispatcher):
        self._dispatchers.append(dispatcher)

    def registerAgent(self, name, host, port):
        self._agents[name] = (host, int(port))
        self._agentslookup[host + ":" + str(port)] = name

    def unregisterAgent(self, name):
        self._agents[name] = None

    def destinationFor (self, parser):
        for dispatcher in self._dispatchers:
            destination = dispatcher.dispatch(parser)
            if destination: return destination

    def agentFor (self, parser):
        destination = self.destinationFor(parser)
        if not destination: return None
        if destination.__class__ is str:
            destination = [destination]
        agents = []
        for peer in destination:
            if peer in self._agents:
                agents.append (self._agents[peer])
        return agents

    def dispatch(self, parser):
        agents = self.agentFor(parser)
        if not agents:
            return
        for agent in agents:
            host, port = agent
            if self._debug:
                self.debugTo(parser, agent)
            self.sendto(host, port, parser.msg())

    def receive(self, parser):
        if not parser.get("_cid"):
            msg = parser.msg()
            cid = str(uuid.uuid4())
            newmsg = MessageBuilder.override(msg, {"_cid":cid}).msg()
            parser = MessageParser(newmsg)
        if self._debug:
            self.debugFrom(parser)
        if parser.get("dst") == "server":
            self.serve(parser)
        else:
            self.dispatch(parser)

    def sendto(self, host, port, message, delay = True):
        try:
            self._listener.send(message, host, port)
            return True
        except Exception as e:
            return False

    def registerAgentDyn(self, parser):
        name = parser.get("name")
        host = parser.get("host")
        port = parser.get("port")
        topic = parser.get("topic")
        self.registerAgent(name, host, port)
        aMap = {"src":"server", "dst":name, "tag":["register", "success"]}
        if topic:
            self._topicdispatcher.add(topic, name)
            aMap["topic"] = topic
        message = MessageBuilder(aMap).msg()
        parser = MessageParser(message)
        self.debugTo(parser, (host, port))
        self.sendto(host, int(port), message)

    def serve(self, parser):
        if "register" in parser.tags():
            self.registerAgentDyn(parser)
        if "unregister" in parser.tags():
            name = parser.get("name")
            topic = parser.get("topic")
            self.unregisterAgent(name)
            if topic:
                self._topicdispatcher.remove(topic, name)

    def debug(self, parser):
        cid = parser.get("_cid")
        keys = list(parser._map.keys())
        keys.sort()
        for key in keys:
            print (cid + "     " + key + " = " + str(parser.get(key)))

    def debugFrom(self, parser):
        cid = parser.get("_cid")
        print(cid + " Message received:")
        self.debug(parser)

    def debugTo(self, parser, agent):
        cid = parser.get("_cid")
        host, port = agent
        print(cid + " Message to " + self._agentslookup[host + ":" + str(port)] + ":")
        self.debug(parser)

