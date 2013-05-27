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

import zoe
import time
import threading

class ListsAgent:
    def __init__(self, interval = 60):
        self._listener = zoe.Listener(self, name = "lists")
        self._model = zoe.Lists()
        self._interval = interval
        self.update()

    def start(self):
        if (self._interval > 0):
            self._resendDaemonThread = threading.Thread (target = self.loop)
            self._resendDaemonThread.start()
        self._listener.start(self.notify)

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        tags = parser.tags()
        if "notify" in tags:
            self.notify(parser)
        if "set" in tags:
            self.setmembers(parser)

    def notify(self, original = None):
        members = self._model.members()
        aMap = {"src":"lists", "topic":"lists", "tag":["lists", "notification"], "book-members":str(members)}
        listnames = []
        lists = self._model.lists()
        for l in lists:
            listnames.append(l)
            aMap["list-" + l + "-members"] = lists[l] 
        aMap["lists"] = listnames
        m = zoe.MessageBuilder(aMap, original).msg()
        self._listener.sendbus(m)
        ingul = len(lists["gul"])
        self._listener.log("lists", "info", "Lists info notified: " + str(ingul) + " in GUL and " + str(members) + " members")

    def update(self):
        self._listener.log("lists", "debug", "Updating lists info")
        self._model.update()
    
    def setmembers(self, parser):
        self._listener.log("lists", "debug", "Updating members info")
        inbook = parser.get("inbook")
        self._model.setmembers(inbook)
        self._listener.log("lists", "info", "Members info updated to " + inbook)
        self.notify(parser)

    def loop(self):
        while True:
            time.sleep(self._interval)
            self.update()
            self.notify()
