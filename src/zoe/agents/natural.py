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
import time
import configparser
import zoe
import pprint
import subprocess

class NaturalAgent:
    def __init__(self):
        self._listener = zoe.Listener(self, name = "natural")
        self.reload()

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def reload(self):
        cmdproc = os.environ["ZOE_HOME"] + "/cmdproc"
        procs = [cmdproc + "/" + f for f in os.listdir(cmdproc)]
        procs = [p for p in procs if os.access(p, os.X_OK)]
        self._commands = {}
        for proc in procs:
            p = subprocess.Popen(proc + " --get", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout.readlines():
                self._commands[line.decode("utf-8")] = proc

        print(self._commands)

    def receive(self, parser):
        tags = parser.tags()
        if "command" in tags:
            self.command(parser)

    def command(self, parser = None):
        cmd = parser.get("cmd")
        analysis = zoe.Fuzzy().analyze(cmd)
        params = self.shellParams(analysis)
        print("[command]", "--stripped", "'" + analysis["stripped"] + "'", "--original", "'" + analysis["original"] + "'", params)

    def shellParams(self, original):
        analysis = dict(original)
        analysis["stripped"] = None
        analysis["original"] = None
        params = ""
        for key in analysis:
            if not analysis[key]:
                continue
            value = analysis[key]
            if value.__class__ is list:
                for value in analysis[key]:
                    if key == "users":
                        value = value["name"]
                    params = params + "--" + key + " '" + value + "' "
            else:
                params = params + "--" + key + " '" + value + "' "
        return params