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

import configparser

class Users:
    def __init__(self, conffile = "zoe-users.conf", confstring = None):
        self._conffile = conffile
        self._confstring = confstring
        self.update()

    def update(self): 
        self._config = configparser.ConfigParser()
        if self._conffile:
            self._config.read(self._conffile, encoding = "utf8")
        else:
            self._config.read_string(self._confstring, encoding = "utf8")
            
    def asmap(self):
        users = {}
        users["subject"] = []
        for section in self._config.sections():
            kind, name = section.split(" ")
            if kind == "group":
                for key in self._config[section]:
                    key2 = "group-" + name + "-" + key
                    value2 = self._config[section][key]
                    if key == "members":
                        value2 = value2.split()
                    users[key2] = value2
            else:
                users["subject"].append(name)
                for key in self._config[section]:
                    users[name + "-" + key] = self._config[section][key]
        return users

    def subjects(self):
        ids = {} 
        for section in self._config.sections():
            kind, name = section.split(" ")
            if kind == "subject":
                aMap = {}
                for key in self._config[section]:
                    aMap[key] = self._config[section][key]
                ids[name] = aMap
        return ids

    def subject(self, name):
        return self._config["subject " + name]

    def group(self, name):
        return self._config["group " + name]

