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

import os
import os.path
import subprocess

class Lists:
    def __init__(self, db = "/tmp/zoe-members"):
        self._db = db
        if not os.path.exists(db):
            self.setmembers(99)
        self.update()

    def update(self):
        self.updatelists()
        self.updatemembers()

    def updatelists(self):
        lists = {}
        cwd=os.getcwd()
        os.chdir("../tareas")
        p = subprocess.Popen('./list_members.sh', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            line = line.decode("utf-8")
            l, m = line.split()
            if not l in lists:
                lists[l] = []
            lists[l].append(m)
        os.chdir(cwd)
        self._lists = lists

    def setmembers(self, n):
        f = open(self._db, "w")
        f.write(str(n))
        f.close()
        self._members = n

    def updatemembers(self):
        f = open(self._db, "r")
        self._members = int(f.read())
        f.close()

    def members(self):
        return self._members

    def lists(self):
        return self._lists

    def find(self, email):
        return [x for x in self._lists if email in self._lists[x]]

