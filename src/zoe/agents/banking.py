import sqlite3
import uuid

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
        if "incoming" in tags:
            self.incoming(parser)
        if "notify" in tags:
            self.notify(parser)

    def opendb(self):
        conn = sqlite3.connect(self._db)
        c = conn.cursor()
        c.execute("create table if not exists m (id text, ts text, amount real, what text)")
        conn.commit()
        return (conn, c)

    def incoming(self, parser):
        ts = parser.get("date")
        amount = parser.get("amount")
        what = parser.get("what")
        self.incoming0(ts, amount, what)

    def incoming0(self, ts, amount, what):
        conn, c = self.opendb()
        params = (str(uuid.uuid4()), ts, amount, what)
        c.execute("insert into m values(?, ?, ?, ?)", params)
        conn.commit()
        c.close()

    def notify(self, parser):
        year = parser.get("year")
        movements = self.movements(year)
        aMap = {"src":"banking", "topic":"banking", "tag":["banking", "notification"]}
        balance = 0
        for movement in movements:
            (uuid, ts, amount, what) = movement
            aMap[uuid + "-date"] = ts
            aMap[uuid + "-amount"] = str(amount)
            aMap[uuid + "-what"] = what
            balance = balance + amount
        aMap["balance"] = str(balance)
        self._listener.sendbus(MessageBuilder(aMap, parser).msg())

    def movements(self, year):
        conn, c = self.opendb()
        params = (year,)
        c.execute("select * from m where strftime('%Y', ts) = ? order by ts", params)
        movements = []
        for row in c:
            (uuid, ts, amount, what) = row
            movements.append((uuid, ts, amount, what))
        c.close()
        return movements
        



