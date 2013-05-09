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
import sys
import re

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

class Fuzzy:

    likelihood = 80

    def __init__(self):
        self._users = zoe.Users()
        self._moneyre = re.compile("([0-9]*[\.,]?[0-9]+)\s*(leuros|euros|euro|eur)", re.IGNORECASE)
        self._stringre = re.compile('\"([^\"]+)\"')
        self._datere = re.compile("(\d\d\d\d-\d\d-\d\d)")
        self._commands = {
            "say hello to <u>": zoe.HelloCmd(None), 
            "say hello from <u> to <u>": zoe.HelloCmd(0), 
            "say hello to <u> from <u>": zoe.HelloCmd(-1), 
            "bank deposit <m> on <d> as <s>": zoe.BankDepositCmd(),
            "bank withdrawal <m> on <d> as <s>": zoe.BankDepositCmd(withdrawal = True),

            "di a <u> por gtalk <s>": zoe.GTalkCmd(),
            "ingreso <m> el día <d> <s>": zoe.BankDepositCmd(), 
            "pago <m> el día <d> <s>": zoe.BankDepositCmd(withdrawal = True),
            "envía la memoria de actividades a <u>": zoe.ActivitiesCmd(),
            "envíame la memoria de actividades": zoe.ActivitiesCmd(tome = True),
            "dame la memoria de actividades": zoe.ActivitiesCmd(tome = True),
           }

    def execute(self, original, context):
        (command, objects) = self.analyze(original)
        objects["context"] = context
        if command:
            return command.execute(objects)

    def analyze(self, original):
        print("Original command: " + original)
       
        cmd = original

        (strings, cmd) = self.extractstrings(cmd)
        print("Found strings: " + str(strings))
        
        (users, cmd) = self.extractusers(cmd)
        print("Found users: " + str(users))
        
        (money, cmd) = self.extractmoney(cmd)
        print("Found money: " + str(money))
        
        (dates, cmd) = self.extractdates(cmd)
        print("Found dates: " + str(dates))
        
        # extract number, ips...
        
        cmd = self.removeduplicates(cmd)
        cmdobjects = {"users":users, "money":money, "strings":strings, 
                      "dates":dates, "original":original, "stripped":cmd}
        
        # try to find a command
        result = process.extract(cmd, self._commands)
        print("Fuzzy matching results:")
        for text, score in result:
            print (text + " => " + str(score))
        text, score = result[0]

        command = None

        # command found

        if score > self.likelihood:
            command = self._commands[text]
        else:
            c = zoe.SmallTalkCmd()
            trial = c.execute(cmdobjects)
            if trial:
                command = c
            
        return (command, cmdobjects)

    def removeduplicates(self, cmd):
        cmd2 = []
        print("Removing duplicates")
        lastword = ""
        for word in cmd.split():
            if word == lastword:
                continue
            lastword = word
            cmd2.append(word)
        return " ".join(cmd2)

    def removespurious(self, cmd):
        trans = str.maketrans(",.", "  ")
        return cmd.casefold().translate(trans)

    def extractusers(self, cmd):
        users = zoe.Users().subjects()
        foundusers = []
        remaining = []
        for word in cmd.split():
            cleanword = self.removespurious(word).strip()
            if cleanword in users.keys() and not word in foundusers:
                foundusers.append(users[cleanword])
                remaining.append("<u>")
            else:
                remaining.append(word)
        
        return (foundusers, " ".join(remaining))

    def regen(self, cmd, start, end, substitution):
        return cmd[:start] + substitution + (" " * (end - start - len(substitution))) + cmd[end:]

    def extractmoney(self, cmd):
        foundamounts = []
        for match in self._moneyre.finditer(cmd):
            amount = (match.group(1), match.group(2))
            foundamounts.append(amount)
            start = match.start()
            end = match.end()
            cmd = self.regen(cmd, start, end, "<m>")
        return (foundamounts, " ".join(cmd.split()))

    def extractstrings(self, cmd):
        foundstrings = []
        for match in self._stringre.finditer(cmd):
            s = match.group(1)
            foundstrings.append(s)
            start = match.start()
            end = match.end()
            cmd = self.regen(cmd, start, end, "<s>")
        return (foundstrings, " ".join(cmd.split()))
    
    def extractdates(self, cmd):
        foundstrings = []
        for match in self._datere.finditer(cmd):
            s = match.group(0)
            foundstrings.append(s)
            start = match.start()
            end = match.end()
            cmd = self.regen(cmd, start, end, "<d>")
        return (foundstrings, " ".join(cmd.split()))

