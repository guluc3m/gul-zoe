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

import zoe

class InventoryAgent:
    def __init__(self, db = None):
        if not db:
            conf = zoe.Config()
            db = conf.db("zoe-inventory.sqlite3")
        self._listener = zoe.Listener(self, name = "inventory")
        self._db = db
        self.notify()

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        tags = parser.tags()
        if "entry" in tags:
            self.entry(parser)
        if "update" in tags:
            self.update(parser)
        if "notify" in tags:
            self.notify(parser)

    def opendb(self):
        conn = sqlite3.connect(self._db)
        c = conn.cursor()
        c.execute("create table if not exists i (id text, amount int, what text)")
        conn.commit()
        return (conn, c)

    def entry(self, parser):
        amount = parser.get("amount")
        what = parser.get("what")
        self.entry0(amount, what)
        self._listener.log("inventory", "info", "inventory updated", parser)

    def entry0(self, amount, what):
        conn, c = self.opendb()
        params = (str(uuid.uuid4()), amount, what)
        c.execute("insert into i values(?, ?, ?)", params)
        conn.commit()
        c.close()

    def notify(self, original = None):
        movements = self.movements()
        aMap = {"src":"inventory", "topic":"inventory", "tag":["inventory", "notification"]}
        ids = []
        for movement in movements:
            (uuid, amount, what) = movement
            aMap[uuid + "-amount"] = str(amount)
            aMap[uuid + "-what"] = what
            ids.append(uuid)
        aMap["ids"] = ids
        self._listener.sendbus(zoe.MessageBuilder(aMap, original).msg())

    def movements(self):
        conn, c = self.opendb()
        c.execute("select * from i where amount > 0")
        movements = []
        for row in c:
            (uuid, amount, what) = row
            movements.append((uuid, amount, what))
        c.close()
        return movements

    def update(self, parser):
        conn, c = self.opendb()
        ident = parser.get("id")
        amount = parser.get("amount")
        if amount == "0" or amount == "none":
            amount = "0"
        c.execute("update i set amount = ? where id = ?", (amount, ident))
        conn.commit()
        c.close()
        self._listener.log("inventory", "info", "inventory entry updated", parser)

