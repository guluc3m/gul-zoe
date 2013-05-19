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
import uuid
import threading
import base64
from datetime import datetime

class BankBalanceCmd:
    def __init__(self, me = True, mail = False):
        self._listener = zoe.Listener(None, None, self, "localhost", 30000, True)
        self._me = me
        self._mail = mail
        self._lock = threading.Lock()
    
    def feedback(self, objects, msg):
        if "feedback" in objects["context"]:
            objects["context"]["feedback"].feedback(msg)

    def execute(self, objects):
        year = zoe.Courses.courseyears()
        self.feedback(objects, "Voy a obtener los movimientos bancarios del curso " + year)

        # Prepare a "get balance" message
        aMap = {"dst":"banking", "tag":"notify", "year":year, "_cid":uuid.uuid4()}
        trigger = zoe.MessageBuilder(aMap).msg()

        # Send the message and stalk topic "banking" for a message from agent "banking" 
        # with the same CID of the trigger message.
        # When the message is received, call self.ready
        # Use a 30 seconds timeout
        msgparams = ("banking", "banking", trigger)
        self._stalker = zoe.StalkerAgent("localhost", 0, "localhost", 30000, msgparams, self.ready, objects, timeout = 30)
        self._stalker.start()
        
        # Synchronize threads
        with self._lock:
            pass

        # Get the memo
        if not "memoparser" in objects:
            self.feedback(objects, "Ha habido un error")
            return objects
        parser = objects["memoparser"]
        memo = self.getmemo(parser)

        # Send the memo
        if self._mail:
            b64 = base64.standard_b64encode(memo.encode('utf-8')).decode('utf-8')
            attachment = zoe.Attachment(b64, "text/html", "balance.html")
            mails = self.mails(objects)
            for u in mails:
                self.feedback(objects, "Enviando la memoria a " + u)
                params = {"dst":"mail", "to":u, "subject":"Movimientos bancarios", "html":attachment.str()}
                msg = zoe.MessageBuilder(params).msg()
                self._listener.sendbus(msg)
            self.feedback(objects, str(datetime.now()) + " - enviado")
        else:
            self.feedback(objects, memo)

    def getmemo(self, parser):
        if self._mail:
            return self.getmemohtml(parser)
        else:
            return self.getmemoplain(parser)

    def getmemoplain(self, parser):
        memo = "Movimientos bancarios generados con fecha: " + str(datetime.now()) + "\n\n"
        ids = parser.get("ids")
        if ids.__class__ is str:
            ids = [ ids ]
        for i in ids:
            date = parser.get(i + "-date")
            amount = parser.get(i + "-amount")
            what = parser.get(i + "-what")
            fmt = "{} {:>10} {}\n"
            entry = fmt.format(date, amount, what)
            memo = memo + entry
        balance = parser.get("balance")
        memo = memo + "\nSaldo actual: " + balance
        return memo

    def getmemohtml(self, parser):
        memo = "<html><body><table><tbody><tr><th>Fecha</th><th>Cantidad</th><th>Concepto</th></tr>"
        ids = parser.get("ids")
        if ids.__class__ is str:
            ids = [ ids ]
        for i in ids:
            date = parser.get(i + "-date")
            amount = parser.get(i + "-amount")
            what = parser.get(i + "-what")
            fmt = "<tr><td>{}</td><td>{}</td><td>{}</td></tr>"
            entry = fmt.format(date, amount, what)
            memo = memo + entry
        memo = memo + "</tbody></table></body></html>"
        balance = parser.get("balance")
        memo = memo + "<br />Saldo actual: " + balance
        return memo

    def mails(self, objects):
        if self._me:
            user = objects["context"]["sender"]
            return [ user["mail"] ]
        else:
            return [ x["mail"] for x in objects["users"] ]

    def ready(self, parser, objects):
        self.feedback(objects, "Ya tengo los movimientos")
        with self._lock:
            objects["memoparser"] = parser
        self._stalker.stop()

BankBalanceCmd.commands = [
    ("dame los movimientos bancarios", BankBalanceCmd(me = True)),
    ("envíame/mándame los movimientos bancarios", BankBalanceCmd(me = True, mail = True)),
]
