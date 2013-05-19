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

class BroadcastAgent:
    def __init__(self):
        conf = zoe.Config()
        port = conf.port("broadcast")
        self._listener = zoe.Listener(port, self)
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
        self._listener.log("broadcast", "info", "Updating users info", parser)

    def requestUsers(self, original = None):
        msg = zoe.MessageBuilder({"dst":"users","tag":"notify"}).msg()
        self._listener.sendbus(msg)
        self._listener.log("broadcast", "info", "Sending users request", original)

    def send(self, parser):
        if not self._parser:
            self.requestUsers(parser)
            return
        msg = parser.get("msg")
        nicks = self._parser.get("group-broadcast-members")
        for nick in nicks:
            preferred = self._parser.get(nick + "-preferred")
            if preferred == "twitter":
                self.tweet(nick, msg, parser)

    def tweet(self, nick, msg, original = None):
        account = self._parser.get(nick + "-twitter")
        tags = {"dst":"twitter", "to":account, "msg":msg}
        self._listener.sendbus(zoe.MessageBuilder(tags, original).msg())
        self._listener.log("broadcast", "info", "Sending message '" + msg + "' to " + account, original)

