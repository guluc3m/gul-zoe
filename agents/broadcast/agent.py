#!/usr/bin/env python3
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
from zoe.deco import *

@Agent(name = "broadcast")
class BroadcastAgent:

    def __init__(self):
        self._users = None

    @Message(tags = ["send"])
    def send(self, msg, to, group = "broadcast", by = None):
        while (not self._users):
            print("Waiting for a users notification...")
            time.sleep(1)
        users = zoe.Users()
        if to:
            return self.sendto(msg, to, users, by)
        else:
            return self.sendgrp(msg, group, users, by)

    @Message(tags = ['users', 'notification'])
    def users(self, parser):
        print("Received users notification")
        self._users = zoe.NetUsers(parser)
        print("Users:", self._users)

    def sendgrp(self, msg, grpname, users, by):
        self.logger.info("Sending message " + msg + " to group " + grpname)
        return [self.sendto(msg, member, users, by) for member in users.membersof(grpname)]

    def sendto(self, msg, user, users, by):
        self.logger.info("Sending message " + msg + " to user " + user)
        subject = users.subject(user)
        preferred = subject["preferred"]
        if not by:
            by = preferred
        if by == "jabber":
            return self.jabber(msg, user)
        elif by == "mail":
            return self.mail(msg, user)
        elif by == "twitter":
            return self.tweet(msg, user)

    def jabber(self, msg, user):
        self.logger.info("Jabber to " + user)
        return zoe.MessageBuilder({"dst":"jabber", "to":user, "msg":msg})
    
    def mail(self, msg, user):
        self.logger.info("Mail to " + user)
        return zoe.MessageBuilder({"dst":"mail", "subject":"Message from Zoe", "to":user, "txt":msg})
        
    def tweet(self, msg, user):
        self.logger.info("Twit to " + user)
        return zoe.MessageBuilder({"dst":"twitter", "to":user, "msg":msg})

