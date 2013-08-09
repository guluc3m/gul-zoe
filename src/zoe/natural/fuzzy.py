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

class FuzzyCmd:
    def execute(self, objects):
        t = ""
        for k in sorted(Fuzzy()._cmdmap.keys()):
            t = t + k + "\n"
        return {"feedback-string":t}

FuzzyCmd.commands = [
    ("ayuda", FuzzyCmd())
]

class Fuzzy:
    
    likelihood = 80
    
    def __init__(self):
        self._users = zoe.Users()
        self._cmdmap = {}
        cmds = [x for x in dir(zoe.natural) if x[-3:] == "Cmd"]
        for cmd in cmds:
            klass = getattr(zoe.natural, cmd)
            self.register(klass)

    def analyze(self, original):
        cmd = original
        strings, cmd = self.extract_strings(cmd)
        integers, cmd = self.extract_integers(cmd)
        floats, cmd = self.extract_floats(cmd)
        users, cmd = self.extract_users(cmd)
        dates, cmd = self.extract_dates(cmd)
        cmd = self.removeduplicates(cmd.lower())
        r = {"users":users, "strings":strings, "integers":integers,
             "dates":dates, "floats":floats, 
             "original":original, "stripped":cmd}
        return r

    def analyze2(self, original):
        cmd = original
        strings, cmd = self.extract_strings(cmd)
        integers, cmd = self.extract_integers(cmd)
        floats, cmd = self.extract_floats(cmd)
        users, cmd = self.extract_users(cmd)
        dates, cmd = self.extract_dates(cmd)
        cmd = self.removeduplicates(cmd.lower())
        r = {"user":[u["id"] for u in users], "string":strings, "integer":integers,
             "date":dates, "float":floats, 
             "original":original, "stripped":cmd}
        return r
    
    def regen(self, cmd, start, end, substitution):
        return cmd[:start] + substitution + cmd[end:]

    def extract(self, cmd, exp, sub):
        exp = re.compile(exp)
        strings = []
        cmd = " " + cmd + " "
        while True:
            s = exp.search(cmd)
            if s:
                start, end = s.span()
                string = s.group(1)
                cmd = cmd[:start] + " " + sub + " " + cmd[end:]
                strings.append(string)
            else:
                break
        return (strings, cmd.strip())

    def extract_strings(self, cmd):
        exp = r'\s\"([^\"]+)\"\s'
        return self.extract(cmd, exp, "<string>")

    def extract_integers(self, cmd):
        exp = r'\s([0-9]+)\s'
        return self.extract(cmd, exp, "<integer>")

    def extract_floats(self, cmd):
        exp = r'\s([0-9]*\.[0-9]+)\s'
        return self.extract(cmd, exp, "<float>")
    
    def extract_dates(self, cmd):
        exp = r'\s(\d\d\d\d-\d\d-\d\d)\s'
        return self.extract(cmd, exp, "<date>")
        
    def removespurious(self, cmd):
        trans = str.maketrans(",.", "  ")
        return cmd.lower().translate(trans)

    def extract_users(self, cmd):
        mailexp = re.compile(r'([^@]+@[^@]+)')
        twitterexp = re.compile(r'(@[^@]+)')
        users = zoe.Users().subjects()
        foundusers = []
        remaining = []
        for word in cmd.split():
            cleanword = self.removespurious(word).strip()
            if cleanword in users.keys() and not word in foundusers:
                foundusers.append(users[cleanword])
                remaining.append("<user>")
            elif mailexp.match(word):
                foundusers.append({"mail":word, "preferred":"mail"})
                remaining.append("<user>")
            elif twitterexp.match(word):
                foundusers.append({"twitter":word, "preferred":"twitter"})
                remaining.append("<user>")
            else:
                remaining.append(word)
        return (foundusers, " ".join(remaining))
    
    def removeduplicates(self, cmd):
        cmd2 = []
        lastword = ""
        for word in cmd.split():
            if word == lastword:
                continue
            lastword = word
            cmd2.append(word)
        return " ".join(cmd2)

    def combinations(self, tokens):
        if len(tokens) == 1:
            return tokens[0]
        else:
            head = tokens[0]
            tail = tokens[1:]
            result = []
            tails = self.combinations(tail)
            for h in head:
                for t in tails:
                    result.append(h + " " + t)
            return result

    def patterns(self, cmd):
        tokens = cmd.split()
        result = []
        for token in tokens:
            syns = token.split("/")
            result.append(syns)
        return self.combinations(result) 
       
    def register(self, klass):
        cmds = klass.commands
        for cmd in cmds:
            pattern, impl = cmd
            for p in self.patterns(pattern):
                q = " ".join(p.split())
                self._cmdmap[q] = impl

    def lookup(self, stripped, amap):
        result = process.extract(stripped, amap)
        #for text, score in result:
        #    print (text + " => " + str(score))
        return result[0]

    def commandfor(self, cmd):
        r = self.analyze(cmd)
        stripped = r["stripped"]
        canonic, score = self.lookup(stripped, self._cmdmap)
        if score > self.likelihood:
            return self._cmdmap[canonic], r
        else:
            return zoe.SmallTalkCmd(), r

    def execute(self, cmd, context = None):
        c, r = self.commandfor(cmd)
        r["context"] = context
        r2 = c.execute(r)
        return r2

