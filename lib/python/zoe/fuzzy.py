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
    
    def __init__(self):
        self._users = zoe.Users()
        self._cmdmap = {}

    def lookup(self, stripped, amap):
        result = process.extract(stripped, amap)
        return result[0]

    def analyze(self, original):
        cmd = original
        strings, cmd = self.extract_strings(cmd)
        urls, cmd = self.extract_urls(cmd)
        symbols, cmd = self.extract_symbols(cmd)
        integers, cmd = self.extract_integers(cmd)
        floats, cmd = self.extract_floats(cmd)
        users, cmd = self.extract_users(cmd)
        dates, cmd = self.extract_dates(cmd)
        mails, cmd = self.extract_mails(cmd)
        twitters, cmd = self.extract_twitter(cmd)
        cmd = self.removeduplicates(cmd.lower())
        r = {"user":[u["id"] for u in users], 
             "string":strings, 
             "integer":integers,
             "date":dates, 
             "float":floats,
             "mail":mails,
             "twitter":twitters,
             "url":urls,
             "symbol":symbols,
             "original":original, 
             "stripped":cmd}
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

    def extract_urls(self, cmd):
        # taken from http://stackoverflow.com/questions/6883049/regex-to-find-urls-in-string-in-python
        exp = r'\s(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)\s'
        return self.extract(cmd, exp, "<url>")
    
    def extract_symbols(self, cmd):
        exp = r'\s:(\w+)\s'
        return self.extract(cmd, exp, "<symbol>")

    def extract_integers(self, cmd):
        exp = r'\s([0-9]+)\s'
        return self.extract(cmd, exp, "<integer>")

    def extract_floats(self, cmd):
        exp = r'\s([0-9]*\.[0-9]+)\s'
        return self.extract(cmd, exp, "<float>")
    
    def extract_dates(self, cmd):
        exp = r'\s(\d\d\d\d-\d\d-\d\d)\s'
        return self.extract(cmd, exp, "<date>")

    def extract_mails(self, cmd):
        exp = re.compile(r'\s([^@\s]+@[^@\s]+)\s')
        return self.extract(cmd, exp, "<mail>")

    def extract_twitter(self, cmd):
        exp = re.compile(r'\s(@[^@\s]+)\s')
        return self.extract(cmd, exp, "<twitter>")

    def removespurious(self, cmd):
        trans = str.maketrans(",.", "  ")
        return cmd.lower().translate(trans)
    
    def extract_users(self, cmd):
        users = zoe.Users().subjects()
        foundusers = []
        remaining = []
        for word in cmd.split():
            cleanword = self.removespurious(word).strip()
            if cleanword in users.keys() and not word in foundusers:
                foundusers.append(users[cleanword])
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
