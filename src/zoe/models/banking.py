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

class Banking:
    def __init__(self, db = "/tmp/zoe-banking.sqlite3"):
        self._db = db

    def opendb(self):
        conn = sqlite3.connect(self._db)
        c = conn.cursor()
        c.execute("create table if not exists m (id text, year text, ts text, amount real, what text)")
        conn.commit()
        return (conn, c)

    def entry(self, year, ts, amount, what):
        conn, c = self.opendb()
        params = (str(uuid.uuid4()), year, ts, amount, what)
        c.execute("insert into m values(?, ?, ?, ?, ?)", params)
        conn.commit()
        c.close()

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

