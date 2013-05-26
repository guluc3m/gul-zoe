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

class InventoryCmd:
    def __init__(self, me = True, mail = False):
        self._listener = zoe.Listener(0, self)
        self._me = me
        self._mail = mail
        self._lock = threading.Lock()
    
    def feedback(self, objects, msg):
        if "feedback" in objects["context"]:
            objects["context"]["feedback"].feedback(msg)

    def execute(self, objects):
        self.feedback(objects, "Voy a obtener el inventario")

        # Prepare a "get balance" message
        aMap = {"dst":"inventory", "tag":"notify", "_cid":uuid.uuid4()}
        trigger = zoe.MessageBuilder(aMap).msg()

        # Send the message and stalk topic "banking" for a message from agent "banking" 
        # with the same CID of the trigger message.
        # When the message is received, call self.ready
        # Use a 30 seconds timeout
        msgparams = ("inventory", "inventory", trigger)
        self._stalker = zoe.StalkerAgent(msgparams, self.ready, objects, timeout = 30)
        self._stalker.start()
        
        # Synchronize threads
        with self._lock:
            pass

        # Get the inventory msg
        if not "memoparser" in objects:
            self.feedback(objects, "Ha habido un error")
            return objects
        parser = objects["memoparser"]
        return self.execute0(objects, parser)

    def mails(self, objects):
        if self._me:
            user = objects["context"]["sender"]
            return [ user["mail"] ]
        else:
            return [ x["mail"] for x in objects["users"] ]

    def ready(self, parser, objects):
        self.feedback(objects, "Ya tengo el inventario")
        with self._lock:
            objects["memoparser"] = parser
        self._stalker.stop()


class QueryInventory(InventoryCmd):
    def __init__(self, me = True, mail = False):
        InventoryCmd.__init__(self, me, mail)
    
    def execute0(self, objects, parser):
        return self.query(objects, parser)

    def query(self, objects, parser):
        memo = self.getmemo(parser)
        if self._mail:
            b64 = base64.standard_b64encode(memo.encode('utf-8')).decode('utf-8')
            attachment = zoe.Attachment(b64, "text/html", "inventory.html")
            mails = self.mails(objects)
            for u in mails:
                self.feedback(objects, "Enviando el inventario a " + u)
                params = {"dst":"mail", "to":u, "subject":"Inventario", "txt64":attachment.str()}
                msg = zoe.MessageBuilder(params).msg()
                self._listener.sendbus(msg)
            self.feedback(objects, "Enviado")
        else:
            self.feedback(objects, memo)

    def getmemo(self, parser):
        memo = "Inventario\n"
        ids = parser.list("ids")
        for i in ids:
            amount = parser.get(i + "-amount")
            what = parser.get(i + "-what")
            fmt = "{:<3} {}\n"
            entry = fmt.format(amount, what)
            memo = memo + entry
        return memo



class AddInventory(InventoryCmd):

    def __init__(self, me = True, mail = False):
        InventoryCmd.__init__(self, me, mail)

    def execute0(self, objects, parser):
        if self._mail:
            return self.addmail(objects, parser)
        else:
            return self.addcmdline(objects, parser)

    def add(self, amount, what, parser):
        aMap = {"dst":"inventory", "tag":"entry", "amount":amount, "what":what}
        msg = zoe.MessageBuilder(aMap, parser).msg()
        self._listener.sendbus(msg)

    def addmail(self, objects, parser):
        bigstring = objects["context"]["bigstring"]
        for line in bigstring.split("\n"):
            tokens = line.split()
            amount = tokens[0]
            sep = line.find(tokens[1])
            what = line[sep:]
            self.add(amount, what, parser)
        return {"feedback-string":"Inventario actualizado"}

    def addcmdline(self, objects, parser):
        amounts = objects["integers"]
        whats = objects["strings"]
        if len(amounts) != len(whats):
            print("I can only handle as many amounts as concepts")
            return {"feedback-string":"Necesito tantas cantidades como conceptos"}
        for i in range(len(amounts)):
            amount = amounts[i]
            what = whats[i]
            self.add(amount, what, parser)
        return {"feedback-string":"Inventario actualizado"}




class UpdateInventory(AddInventory):

    def __init__(self, me = True, mail = False):
        AddInventory.__init__(self, me, mail)

    def execute0(self, objects, parser):
        self.drop(objects, parser)
        return self.addmail(objects, parser)
        
    def drop(self, objects, parser):
        ids = parser.list("ids")
        for i in ids:
            if i:
                aMap = {"dst":"inventory", "tag":"update", "id":i, "amount":"none"}
                msg = zoe.MessageBuilder(aMap, parser).msg()
                self._listener.sendbus(msg)





InventoryCmd.commands = [
    ("dame el inventario", QueryInventory(me = True, mail = False)),
    ("envíame/mándame el inventario", QueryInventory(me = True, mail = True)),
    ("envía/manda el inventario a <user>", QueryInventory(me = False, mail = True)),
    ("actualiza el inventario", UpdateInventory(me = True, mail = True)),
    ("añade al inventario", AddInventory(me = True, mail = True)),
    ("añade al inventario <integer> <string>", AddInventory(me = True, mail = False))
]
