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

class BankDepositCmd:
    def __init__(self, withdrawal = False):
        self._listener = zoe.Listener(None, None, self, "localhost", 30000, True)
        self._withdrawal = withdrawal

    def execute(self, objects):
        money = objects["floats"] + objects["integers"]
        concepts = objects["strings"]
        dates = objects["dates"]
        
        if len(money) != len(concepts):
            print("I can only handle as many amounts as concepts")
            return {"feedback-string":"Necesito tantas cantidades como conceptos"}

        if len(dates) != 1 and len(dates) != len(money):
            print("I can only handle 1 date or as many as amounts")
            return {"feedback-string":"Necesito una única fecha, o una por concepto"}

        for i in range(len(money)):
            amount = money[i]
            what = concepts[i]

            if len(dates) == 1:
                date = dates[0]
            else:
                date = dates[i]

            if self._withdrawal:
                amount = "-" + amount

            print("bank entry on " + date + ": " + amount + " as " + what)
            params = {"dst":"banking", "tag":"entry", "date":date, "amount":amount, "what":what}
            msg = zoe.MessageBuilder(params).msg()
            self._listener.sendbus(msg)
            return {"feedback-string":"Ingreso de " + amount + " realizado"}

BankDepositCmd.commands = [
    ("ingreso /de <float> /el /día <date> <string>", BankDepositCmd()), 
    ("pago /de <float> /el /día <date> <string>", BankDepositCmd(withdrawal = True)),
]
