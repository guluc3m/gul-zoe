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

import uuid
import datetime
import base64
import zoe
import time

class BankingAgent:
    def __init__(self, db = None):
        if not db:
            conf = zoe.Config()
            db = conf.db("zoe-banking.sqlite3")
        self._listener = zoe.Listener(self, name = "banking")
        self._model = zoe.Banking(db)

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        tags = parser.tags()
        if "entry" in tags:
            self.entry(parser)
        if "notify" in tags:
            self.notify(parser.get("year"), parser)
        if "memo" in tags:
            self.memo(parser)
        if "check" in tags:
            self.check(parser)

    def entry(self, parser):
        y = parser.get("year")
        ts = parser.get("date")
        account = parser.get("account")
        amount = parser.get("amount")
        what = parser.get("what")
        if not y or y == "":
            y2, m2, d2 = ts.split("-")
            y = zoe.Courses.courseyears(y2, m2)
        self._model.entry(y, ts, account, amount, what)
        self._listener.log("banking", "info", "New entry: " + y + ", " + ts + ", " + account + ", " + str(amount) + ", " + what, parser)
        self.notify(y, parser)

    def notify(self, year, original = None):
        movements = self._model.movements(year)
        aMap = {"src":"banking", "topic":"banking", "tag":["banking", "notification"], "year":str(year)}
        ids = []
        balance = 0
        for movement in movements:
            (uuid, year, ts, account, amount, what) = movement
            aMap[uuid + "-year"] = year
            aMap[uuid + "-date"] = ts
            aMap[uuid + "-account"] = account
            aMap[uuid + "-amount"] = str(amount)
            aMap[uuid + "-what"] = what
            balance = balance + amount
            ids.append(uuid)
        aMap["balance"] = str(balance)
        aMap["ids"] = ids
        self._listener.sendbus(zoe.MessageBuilder(aMap, original).msg())
        self._listener.log("banking", "info", "Sending banking notification for year " + str(year), original)

    def memo(self, parser):
        movements = self.getmovements(parser)
        print(self.getmemoplain(movements))
        data = self.getmemohtml(movements).encode("utf-8")
        b64 = base64.standard_b64encode(data).decode('utf-8')
        attachment = zoe.Attachment(b64, "text/html", "movements.html")
        aMap = {"src":"banking", "topic":"banking", "tag":["generated-memo", "html"], "memo":attachment.str()}
        msg = zoe.MessageBuilder(aMap, parser).msg()
        self._listener.sendbus(msg)
        self._listener.log("banking", "info", "HTML memo generated", parser)
        recipient = parser.get("mail")
        if not recipient:
            return
        aMap = {"src":"banking", "dst":"mail", "to":recipient, "subject":"Banking memo", "html":attachment.str()}
        msg = zoe.MessageBuilder(aMap, parser).msg()
        self._listener.sendbus(msg)
        self._listener.log("banking", "info", "HTML memo mailed to " + recipient, parser)

    def getmovements(self, parser):
        year = parser.get("year")
        if not year:
            year = zoe.Courses.courseyears()
        print("Voy a mostrarte los movimientos del año", year)
        movements = self._model.movements(year)
        account = parser.get("account")
        if account:
            print("Voy a quedarme con la cuenta", account)
            movements = [m for m in movements if m[3] == account] # would be nice if this filter was done by sqlite
        return movements

    def getmemoplain(self, movements):
        m = "Movimientos bancarios: \n\n"
        balance = 0
        for movement in movements:
            (uuid, year, date, account, amount, what) = movement
            balance = balance + amount
            fmt = "{} {} {:>10} {:>10} {}\n"
            entry = fmt.format(uuid, date, account, amount, what)
            m = m + entry
        m = m + "\nSaldo actual: " + str(balance)
        return m

    def getmemohtml(self, movements):
        m = "<html><body><table><tbody><tr><th>ID</th><th>Fecha</th><th>Cuenta</th><th>Cantidad</th><th>Concepto</th></tr>"
        balance = 0
        for movement in movements:
            (uuid, year, date, account, amount, what) = movement
            balance = balance + amount
            fmt = "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>"
            entry = fmt.format(uuid, date, account, amount, what)
            m = m + entry
        m = m + "</tbody></table>"
        m = m + "<p>Saldo actual:" + str(balance) + "</p>"
        m = m + "</body></html>"
        return m

    def check(self, parser):
        movements = self.getmovements(parser)
        balance = 0
        expected = float(parser.get("balance"))
        account = parser.get("account")
        for movement in movements:
            (uuid, year, date, account, amount, what) = movement
            balance = balance + amount

        balance = "%.2f" % balance
        expected = "%.2f" % expected

        print("El balance de la cuenta", parser.get("account"), "es", balance)
        print("El balance esperado es", expected)
        match = expected == balance
        print("son iguales?", match)
        if match:
            self.alert("Banking: todo OK", "Te informo de que el balance de las cuentas es el esperado", parser)
        else:
            self.alert("Banking: algo va mal", "Parece que hay un problema con las cuentas del banco", parser)

    def alert(self, subject, message, parser):
        aMap = {"src":"banking", "dst":"broadcast", "tag":"send", "msg":message, "subject":subject}
        msg = zoe.MessageBuilder(aMap, parser).msg()
        self._listener.sendbus(msg)
        self._listener.log("banking", "info", "Broadcasting message " + message, parser)

