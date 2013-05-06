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

import sqlite3
import uuid
import datetime

from zoe.zs import *

class BankingAgent:
    def __init__(self, host, port, serverhost, serverport, db = "/tmp/zoe-banking.sqlite3"):
        self._listener = Listener(host, port, self, serverhost, serverport)
        self._db = db

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

    def opendb(self):
        conn = sqlite3.connect(self._db)
        c = conn.cursor()
        c.execute("create table if not exists m (id text, year text, ts text, amount real, what text)")
        conn.commit()
        return (conn, c)

    def entry(self, parser):
        y = parser.get("year")
        ts = parser.get("date")
        amount = parser.get("amount")
        what = parser.get("what")
        self.entry0(y, ts, amount, what)

    def entry0(self, year, ts, amount, what):
        conn, c = self.opendb()
        params = (str(uuid.uuid4()), year, ts, amount, what)
        c.execute("insert into m values(?, ?, ?, ?, ?)", params)
        conn.commit()
        c.close()

    def notify(self, year, original = None):
        movements = self.movements(year)
        aMap = {"src":"banking", "topic":"banking", "tag":["banking", "notification"], "year":str(year)}
        ids = []
        balance = 0
        for movement in movements:
            (uuid, year, ts, amount, what) = movement
            aMap[uuid + "-year"] = year
            aMap[uuid + "-date"] = ts
            aMap[uuid + "-amount"] = str(amount)
            aMap[uuid + "-what"] = what
            balance = balance + amount
            ids.append(uuid)
        aMap["balance"] = str(balance)
        aMap["ids"] = ids
        self._listener.sendbus(MessageBuilder(aMap, original).msg())

    def movements(self, year):
        conn, c = self.opendb()
        params = (year,)
        c.execute("select * from m where year = ? order by ts", params)
        movements = []
        for row in c:
            (uuid, year2, ts, amount, what) = row
            movements.append((uuid, year, ts, amount, what))
        c.close()
        return movements
        



