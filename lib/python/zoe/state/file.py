# -*- coding: utf-8 -*-
#
# This file is part of Zoe Assistant - https://github.com/guluc3m/gul-zoe
#
# Copyright (c) 2014 David Muñoz Díaz <david@gul.es> 
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
import os

class Stuff:

    def all(category):
        res = []
        try:
            print("Looking for all stuff in category", category)
            directory = os.environ['ZOE_HOME'] + "/var/state/stuff/" + category
            for sender in os.listdir(directory):
                for ident in os.listdir(directory + "/" + sender):
                    res.append((sender, ident))
        except OSError as e:
            pass
        return res

    def __init__(self, sender, category, ident):
        self._sender = sender
        self._category = category
        self._ident = ident
        self._directory = os.environ['ZOE_HOME'] + "/var/state/stuff/" + category + "/" + sender
        self._filename = self._directory +  "/" + self._ident
        try:
            os.makedirs(self._directory)
        except OSError as e:
            pass
        
    def write(self, text):
        f = open(self._filename, "w")
        f.write(text)
        f.close()

    def read(self):
        f = open(self._filename, "rb")
        data = f.read()
        f.close()
        return data

    def remove(self):
        try:
            os.remove(self._filename)
        except OSError as e:
            pass
    
    def text(self):
        f = open(self._filename, "r")
        data = f.read()
        f.close()
        return data

    def list(self):
        return os.listdir(self._directory)

