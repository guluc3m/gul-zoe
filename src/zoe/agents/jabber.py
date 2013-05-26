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
import sleekxmpp
import time
from datetime import datetime

class JabberSession:
    def __init__(self, to, send):
        self._to = to
        self._send = send

    def feedback(self, msg):
        self._send(mto=self._to, mbody=msg, mtype='chat')

class JabberAgent (sleekxmpp.ClientXMPP):
    def __init__(self, jabberhost, jabberport, jabberuser, jabberpassword):
        sleekxmpp.ClientXMPP.__init__(self, jabberuser, jabberpassword)
        conf = zoe.Config()
        port = conf.port("jabber")
        self._listener = zoe.Listener(port, self)
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("ssl_invalid_cert", self.ssl_invalid_cert)
        self.add_event_handler("message", self.messagefromjabber)
        if self.connect((jabberhost, jabberport)):
            self.process(block=False)
            self.start()
        else:
            print('Unable to connect to jabber')

    def ssl_invalid_cert(self, cert_module):
        print("Invalid cert. I'll trust you anyway.")

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def messagefromjabber(self, msg):
        if msg['type'] in ('chat', 'normal'):
            text = msg["body"]
            jid = msg["from"]
            sender = self.finduser(jid)
            js = JabberSession(jid, self.send_message)
            context = {"sender":sender, "feedback":js}
            ret = zoe.Fuzzy().execute(text, context)
            print("RET", ret)
            if ret and "feedback-string" in ret:
                msg.reply(ret["feedback-string"]).send()

    def finduser(self, jid):
        user = jid.user + "@" + jid.domain
        model = zoe.Users()
        subjects = model.subjects()
        for s in subjects:
            if "jabber" in subjects[s] and subjects[s]["jabber"] == user:
                return subjects[s]

    def receive(self, parser):
        to = parser.get("to")
        msg = parser.get("msg")
        print ("Sending " + msg + " to " + to)
        self.send_message(mto=to, mbody=msg)
