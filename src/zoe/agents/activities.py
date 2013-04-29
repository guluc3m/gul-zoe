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
        presi = parser.get(parser.get("group-junta-presi") + "-name")
        vice = parser.get(parser.get("group-junta-vice") + "-name")
        coord = parser.get(parser.get("group-junta-coord") + "-name")
        tesorero = parser.get(parser.get("group-junta-tesorero") + "-name")
        vocal = parser.get(parser.get("group-junta-vocal") + "-name")
        self._users = {"presi":presi, "vice":vice, "tesorero":tesorero, "coord":coord, "vocal":vocal}

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
        print (self._users["presi"])
        print (self._users["vice"])
        print (self._users["coord"])
        print (self._users["tesorero"])
        print (self._users["vocal"])

