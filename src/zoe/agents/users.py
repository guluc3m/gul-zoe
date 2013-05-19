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

import time
import threading
import configparser
import zoe

class UsersAgent:
    def __init__(self, interval = 1, db = None):
        conf = zoe.Config()
        port = conf.port("users")
        if not db:
            db = conf.conf("zoe-users.conf")
        self._listener = zoe.Listener(port, self, debugmode = True)
        self._model = zoe.Users(db)
        self._interval = interval
        self.update()

    def update(self):
        self._model.update()
        self.notify()

    def start(self):
        if (self._interval > 0):
            self._resendDaemonThread = threading.Thread (target = self.loop)
            self._resendDaemonThread.start()
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        tags = parser.tags()
        if "notify" in tags:
            self.notify(parser)

    def notify(self, original = None):
        users = self._model.asmap()
        tags = ["users", "notification"]
        aMap = {"src": "users", "topic": "users", "tag": tags}
        msg = zoe.MessageBuilder(dict(aMap, **users), original).msg()
        self._listener.sendbus(msg)
        
    def loop(self):
        while True:
            time.sleep(self._interval)
            self.update()

