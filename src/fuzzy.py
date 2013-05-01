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

import cmd
import zoe
import sys
import re

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

commands = {
            "say hello to": zoe.HelloCmd(None), 
            "say hello from to": zoe.HelloCmd(0), 
            "say hello to from": zoe.HelloCmd(-1), 
            "bank deposit on as": zoe.BankDepositCmd(),
            "bank withdrawal on as": zoe.BankDepositCmd(withdrawal = True),
           }

class Lexer:

    likelihood = 80

    def __init__(self):
        self._users = zoe.Users()
        self._moneyre = re.compile("([0-9]*[\.,]?[0-9]+)\s*(leuros|euros|euro|eur)", re.IGNORECASE)
        self._stringre = re.compile('\"([^\"]+)\"')
        self._datere = re.compile("(\d\d\d\d-\d\d-\d\d)")

    def analyze(self, original):
        print("Original command: " + original)
        (users, cmd) = self.extractusers(original)
        print("Found users: " + str(users))
        (money, cmd) = self.extractmoney(cmd)
        print("Found money: " + str(money))
        (strings, cmd) = self.extractstrings(cmd)
        print("Found strings: " + str(strings))
        (dates, cmd) = self.extractdates(cmd)
        print("Found dates: " + str(dates))
        
        # extract number, ips...
        
        print("Stripped command: " + str(cmd))
        result = process.extract(cmd, commands)
        print("Fuzzy matching results:")
        for text, score in result:
            print (text + " => " + str(score))
        text, score = result[0]
        if score < self.likelihood:
            return (None, None)
        command = commands[text]
        cmdobjects = {"users":users, "money":money, "strings":strings, "dates":dates}
        return (command, cmdobjects)

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
            else:
                remaining.append(word)
        return (foundusers, " ".join(remaining))

    def extractmoney(self, cmd):
        foundamounts = []
        for match in self._moneyre.finditer(cmd):
            amount = (match.group(1), match.group(2))
            foundamounts.append(amount)
            start = match.start()
            end = match.end()
            cmd = cmd[:start] + (" " * (end - start)) + cmd[end:]
        return (foundamounts, " ".join(cmd.split()))

    def extractstrings(self, cmd):
        foundstrings = []
        #trans = str.maketrans("\"", "'")
        #cmd = cmd.translate(trans)
        for match in self._stringre.finditer(cmd):
            s = match.group(1)
            foundstrings.append(s)
            start = match.start()
            end = match.end()
            cmd = cmd[:start] + (" " * (end - start)) + cmd[end:]
        return (foundstrings, " ".join(cmd.split()))
    
    def extractdates(self, cmd):
        foundstrings = []
        for match in self._datere.finditer(cmd):
            s = match.group(0)
            foundstrings.append(s)
            start = match.start()
            end = match.end()
            cmd = cmd[:start] + (" " * (end - start)) + cmd[end:]
        return (foundstrings, " ".join(cmd.split()))


class FuzzyShell(cmd.Cmd):

    prompt = "zoe> "

    def default(self, line):
        lex = Lexer()
        command, objs = lex.analyze(line)
        if not command:
            print("Sorry I don't understand you.")
            return
        print("Chosen command: " + str(command))
        print("Objects: " + str(objs))
        command.execute(objs)

    def do_EOF(self, line):
        return True

shell = FuzzyShell()
cmd = " ".join(sys.argv[1:])
if (cmd):
    shell.default(cmd)
else:
    shell.cmdloop()


