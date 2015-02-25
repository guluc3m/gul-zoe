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

import uuid

class MessageParser:
    def __init__(self, msg, addr = None):
        self._msg = msg.strip()
        self._map = {}
        self._addr = addr
        pairs = msg.split("&")
        for pair in pairs:
            if pair == "":
                continue
            p = pair.find("=")
            key = pair[:p]
            value = pair[p + 1:].strip()
            if key in self._map:
                current = self._map[key]
                if current.__class__ is list:
                    self._map[key].append(value)
                else:
                    self._map[key] = [current, value]
            else:
                self._map[key] = value

    def msg(self):
        return self._msg

    def get(self, key):
        if key in self._map:
            return self._map[key]
        else:
            return None

    def list(self, key):
        r = self.get(key)
        if not r.__class__ is list:
            r = [r]
        return [x for x in r if x]

    def tags(self):
        return self.list("tag")

    def addr(self):
        return self._addr
        
    def __str__(self):
        return str(self._map)

class MessageBuilder:

    def __init__(self, aMap, original = None):
        if not "_cid" in aMap:
            if original and original.get("_cid"):
                aMap["_cid"] = original.get("_cid")
            else:
                aMap["_cid"] = str(uuid.uuid4())
        aStr=""
        for key in aMap.keys():
            value = aMap[key]
            if not value:
                continue
            if value.__class__ is str:
                aStr = aStr + key + "=" + value + "&"
            else:
                for v in value:
                    aStr = aStr + key + "=" + v + "&"
        if aStr[-1] == "&":
            aStr = aStr[:-1]
        self._msg = aStr
        self._map = aMap

    def fromparser (original):
        return MessageBuilder(original._map, original)

    def override (original, aMap):
        mp = None
        if original.__class__ is str:
            mp = MessageParser(original)
        else:
            mp = original
        newMap = dict(mp._map, **aMap)
        return MessageBuilder(newMap)

    def put(self, key, value):
        newMap = dict(self._map, **{ key : value })
        return MessageBuilder(newMap)

    def msg(self):
        return self._msg
        
    def __str__(self):
        return self._msg

