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

from zoe.zs import *
import uuid
import sys

class StalkerAgent:
    def __init__(self, host, port, serverhost, serverport, msgparams, callback):
        self._listener = Listener(host, port, self, serverhost, serverport)
        self._source, self._topic, self._original = msgparams
        self._name = "stalker-" + str(uuid.uuid4())
        self._parser = MessageParser(self._original)
        self._callback = callback

    def start(self):
        self._listener.start(self.register)

    def stop(self):
        self.unregister()
        self._listener.stop()

    def receive(self, parser):
        tags = parser.tags()
        source = parser.get("src")
        cid = parser.get("_cid")
        if source == self._source and cid == self._parser.get("_cid"):
            self._callback(parser)
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


