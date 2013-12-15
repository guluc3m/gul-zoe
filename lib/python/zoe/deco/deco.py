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
import inspect

class DecoratedLogger:

    def __init__(self, listener, name, parser):
        self._listener = listener
        self._name = name
        self._parser = parser
        
    def log(self, level, msg):
        self._listener.log(self._name, level, msg, self._parser)    
    
    def info(self, msg):
        self.log("info", msg)

    def debug(self, msg):
        self.log("debug", msg)

    def warn(self, msg):
        self.log("WARNING", msg)

    def error(self, msg):
        self.log("ERROR", msg)


class DecoratedListener:
    def __init__(self, agent, name):
        self._agent = agent
        self._name = name
        self._candidates = []
        for m in dir(agent):
            k = getattr(agent, m)
            if hasattr(k, "__zoe__tags__"):
                self._candidates.append(k)
        print("Launching agent", self._name)
        self._listener = zoe.Listener(self, name = self._name)
        self._listener.start()

    def receive(self, parser):
        print("received", str(parser))
        tags = parser.tags()
        self.dispatch(tags, parser)

    def dispatch(self, tags, parser):
        chosen = []
        for c in self._candidates:
            expected = c.__zoe__tags__
            if self.match(tags, expected):
                chosen.append(c)
        if len(chosen) == 0:
            print("No candidates found")
            return
        if len(chosen) > 1:
            print("Too many candidates found")
            for c in chosen:
                print(c, c.__zoe__tags__)
            return
        print("Candidate found:", c, "given", tags, "expected", c.__zoe__tags__)
        self.docall(c, parser)

    def match(self, tags, expected):
        for t in expected:
            if not t in tags:
                return False
        return True

    def docall(self, method, parser):
        print("Calling method", method, "with parameters", parser)
        args, varargs, keywords, defaults = inspect.getargspec(method)
        args = args[1:]
        params = []
        for arg in args:
            if arg == "parser":
                param = parser
            elif arg == "logger":
                param = DecoratedLogger(self._listener, self._name, parser)
            elif parser.get(arg):
                param = parser.get(arg)
            else:
                param = None
            params.append(param)
        ret = method(*params)
        if ret:
            if not hasattr(ret, "__iter__"):
                ret = [ret]
            for r in ret:
                rep = str(r)
                print(rep)
                self._listener.sendbus(rep)

class Message:
    def __init__(self, tags):
        self._tags = tags

    def __call__(self, f):
        setattr(f, "__zoe__tags__", self._tags)
        return f

class Agent:
    def __init__(self, name):
        self._name = name

    def __call__(self, i):
        DecoratedListener(i(), self._name)

