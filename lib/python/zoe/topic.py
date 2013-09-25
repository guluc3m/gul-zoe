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


class TopicDispatcher:
    def __init__(self, config):
        self._topics = {}
        self._config = config
        self.registerTopics()

    def registerTopics(self):
        for section in self._config.sections():
            sectype, name = section.split(" ")
            if sectype == "topic":
                agents = self._config[section]["agents"].split(" ")
                self.add (name, *agents)

    def descr(self):
        return "Topic dispatcher"

    def add(self, topic, *names):
        if not topic in self._topics:
            self._topics[topic] = []
        for name in names:
            self._topics[topic].append(name)

    def remove(self, topic, *names):
        if not topic in self._topics:
            return
        for name in names:
            if name in self._topics[topic]:
                self._topics[topic].remove(name)

    def dispatch(self, parser):
        tname = parser.get("topic")
        if not tname: return None
        if not tname in self._topics: return None
        agents = list(self._topics[tname])
        src = parser.get("src")
        if src and src in agents:
            agents.remove(src)
        return agents
