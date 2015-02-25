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

import pprint
import zoe
import sleekxmpp
import time
import sys
import base64
from datetime import datetime

class JabberAgent (sleekxmpp.ClientXMPP):
    def __init__(self, jabberhost, jabberport, jabberuser, jabberpassword):
        sleekxmpp.ClientXMPP.__init__(self, jabberuser, jabberpassword)
        self._listener = zoe.Listener(self, name = "jabber")
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
        print("msg = ", msg)
        if not (msg['type'] in ('chat', 'normal')):
            self._listener.log("jabber", "WARNING", "received an unknown jabber message type")
            return
        text = msg["body"]
        jid = msg["from"]
        sender = self.finduser(jid)
        if not sender: 
            self._listener.log("jabber", "WARNING", "received a jabber message from an unknown user")
            msg.reply("Lo siento, no me permiten hablar con desconocidos").send()
            return
        text64 = base64.standard_b64encode(text.encode('utf-8')).decode('utf-8')
        aMap = {"dst":"relay",
                "relayto":"natural", 
                "src":"jabber", 
                "tag":["command", "relay"],
                "sender":sender["id"],
                "jid":str(jid),
                "cmd":text64}
        self._listener.log("jabber", "DEBUG", "Relaying the jabber message to the natural agent")
        self._listener.sendbus(zoe.MessageBuilder(aMap).msg())

    def finduser(self, jid):
        user = jid.user + "@" + jid.domain
        model = zoe.Users()
        subjects = model.subjects()
        for s in subjects:
            if "jabber" in subjects[s] and user in subjects[s]["jabber"].split(","):
                return subjects[s]

    def receive(self, parser):
        if "command-feedback" in parser.tags():
            self.feedback(parser)
        else:
            self.sendmsg(parser)
    
    def feedback(self, parser):
        jid = parser.get("jid")
        txt = parser.get("feedback-string")
        self.send_message(mto = jid, mbody = txt, mtype = 'chat')

    def guess(self, dest):
        if "@" in dest:
            return dest
        subjects = zoe.Users().subjects()
        if dest in subjects:
            address = subjects[dest]["jabber"]
            if "," in address:
                address = address.split(",")[0]
            return address
        
    def sendmsg(self, parser):
        to = self.guess(parser.get("to"))
        msg = parser.get("msg")
        print ("Sending " + msg + " to " + to)
        self._listener.log("jabber", "DEBUG", "Sending " + msg + " to " + to)
        self.send_message(mto = to, mbody = msg, mtype = 'chat')

