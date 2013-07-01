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

class BankBalanceBasedCommand:
    def __init__(self):
        self._listener = zoe.Listener(self, port = 0)
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
        self._stalker = zoe.StalkerAgent(msgparams, self.ready, objects, timeout = 30)
        self._stalker.start()
        
        # Synchronize threads
        with self._lock:
            pass

        # Get the memo
        if not "memoparser" in objects:
            self.feedback(objects, "Ha habido un error")
            return objects

        return self.command(objects)
    
    def getmemo(self, parser, filteraccount = None):
        movements = []
        ids = parser.list("ids")
        mybalance = 0
        for i in ids:
            account = parser.get(i + "-account")
            if not filteraccount or filteraccount == account:
                date = parser.get(i + "-date")
                amount = parser.get(i + "-amount")
                what = parser.get(i + "-what")
                entry = (date, account, amount, what)
                movements.append(entry)
                mybalance = mybalance + float(amount)
        balance = parser.get("balance")
        memo = {"movements":movements, "balance":balance, "localbalance":mybalance} 
        return memo
        
    def ready(self, parser, objects):
        self.feedback(objects, "Ya tengo los movimientos")
        with self._lock:
            objects["memoparser"] = parser
        self._stalker.stop()        
    
class BankBalanceCmd(BankBalanceBasedCommand):
    def __init__(self, me = True, mail = False, givenaccount = False):
        BankBalanceBasedCommand.__init__(self)
        self._me = me
        self._mail = mail
        self._givenaccount = givenaccount

    def command(self, objects):
        parser = objects["memoparser"]
        if self._givenaccount:
            self._account = objects["strings"][0]
            self.feedback(objects, "Voy a considerar la cuenta " + self._account)
        else:
            self._account = None
        memo = self.textmemo(parser)
        if self._mail:
            b64 = base64.standard_b64encode(memo.encode('utf-8')).decode('utf-8')
            attachment = zoe.Attachment(b64, "text/html", "balance.html")
            mails = self.mails(objects)
            for u in mails:
                self.feedback(objects, "Enviando la memoria a " + u)
                params = {"dst":"mail", "to":u, "subject":"Movimientos bancarios", "html":attachment.str()}
                msg = zoe.MessageBuilder(params).msg()
                self._listener.sendbus(msg)
            self.feedback(objects, "Enviado")
        else:
            self.feedback(objects, memo)

    def textmemo(self, parser):
        memo = self.getmemo(parser, self._account)
        if self._mail:
            generator = self.getmemohtml
        else:
            generator = self.getmemoplain
        return generator(memo)

    def getmemoplain(self, memo):
        m = "Movimientos bancarios: \n\n"
        for date, account, amount, what in memo["movements"]:
            fmt = "{} {:>10} {:>10} {}\n"
            entry = fmt.format(date, account, amount, what)
            m = m + entry
        m = m + "\nSaldo actual: " + memo["balance"]
        m = m + "\nSaldo calculado: " + str(memo["localbalance"])
        return m

    def getmemohtml(self, memo):
        m = "<html><body><table><tbody><tr><th>Fecha</th><th>Cuenta</th><th>Cantidad</th><th>Concepto</th></tr>"
        for date, account, amount, what in memo["movements"]:
            fmt = "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>"
            entry = fmt.format(date, account, amount, what)
            m = m + entry
        m = m + "</tbody></table></body></html>"
        m = m + "<br />Saldo actual: " + memo["balance"]
        m = m + "<br />Saldo calculado: " + str(memo["localbalance"])
        return m

    def mails(self, objects):
        if self._me:
            user = objects["context"]["sender"]
            return [ user["mail"] ]
        else:
            return [ x["mail"] for x in objects["users"] ]

class CheckAccountBalanceCmd(BankBalanceBasedCommand):
    def __init__(self, mail = False):
        BankBalanceBasedCommand.__init__(self)
        self._mail = mail
        
    def command(self, objects):
        parser = objects["memoparser"]
        numbers = objects["integers"] + objects["floats"] 
        account = objects["strings"][0]
        memo = self.getmemo(parser, account)
        localbalance = memo["localbalance"]
        expectedbalance = float(numbers[0])
        if localbalance == expectedbalance:
            msg = "El balance de la cuenta %s es el esperado, %0.2f" % (account, expectedbalance)
            code = 0
        else:
            msg = "El balance de la cuenta %s _no_ cuadra. Me dicen que debería ser %0.2f pero obtengo %0.2f" % (account, expectedbalance, localbalance)
            code = 1
        if self._mail:
            self.sendmail(msg)
            self.feedback(objects, "Mensaje enviado");
        else:
            self.feedback(objects, msg)
        return {"return-code":code}

    def sendmail(self, msg):
        params = {"dst":"broadcast", "tag":"send", "group":"banking", "msg":msg}
        msg = zoe.MessageBuilder(params).msg()
        self._listener.sendbus(msg)


BankBalanceCmd.commands = [
    ("dame los movimientos bancarios", BankBalanceCmd(me = True)),
    ("dame los movimientos /bancarios de la cuenta <string>", BankBalanceCmd(me = True, givenaccount = True)),
    ("envíame/mándame los movimientos bancarios", BankBalanceCmd(me = True, mail = True)),
    ("envíame/mándame los movimientos /bancarios de la cuenta <string>", BankBalanceCmd(me = True, mail = True, givenaccount = True)),
    ("envía los movimientos bancarios a <user>", BankBalanceCmd(me = False, mail = True)),
    ("envía los movimientos /bancarios de la cuenta <string> a <user>", BankBalanceCmd(me = False, mail = True, givenaccount = True)),
]

CheckAccountBalanceCmd.commands = [
    ("el balance de la cuenta <string> debería ser <float>/<integer>", CheckAccountBalanceCmd()),
    ("comprueba que el balance de la cuenta <string> es/sea <float>/<integer>", CheckAccountBalanceCmd()),
    ("notifica/email si el balance de la cuenta <string> es <float>/<integer>", CheckAccountBalanceCmd(mail = True))
]
