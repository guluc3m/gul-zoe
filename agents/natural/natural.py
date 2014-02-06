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
import subprocess
import base64
import tempfile
import json

class NaturalAgent:

    likelihood = 80

    def __init__(self):
        self._listener = zoe.Listener(self, name = "natural")

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def show(self, title, thing):
        print(title, json.dumps(thing, sort_keys = True, indent = 4))

    def reload(self):
        fuzzy = zoe.Fuzzy()
        cmdproc = os.environ["ZOE_HOME"] + "/cmdproc"
        procs = [cmdproc + "/" + f for f in os.listdir(cmdproc)]
        procs = [p for p in procs if os.access(p, os.X_OK)]
        self._commands = {}
        for proc in procs:
            p = subprocess.Popen(proc + " --get", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout.readlines():
                pattern = line.decode("utf-8")
                for p in fuzzy.patterns(pattern):
                    proccommand = []
                    procparams = []
                    for word in p.split():
                        if word[0:2] == "--":
                            procparams.append(word)
                        else:
                            proccommand.append(word)
                    self._commands[" ".join(proccommand)] = (proc, procparams)

    def receive(self, parser):
        tags = parser.tags()
        if "command" in tags:
            self.command(parser)

    def command(self, parser):
        self.reload()
        self.show("Received parser:", parser._map)
        cmd64 = parser.get("cmd")
        cmd = base64.standard_b64decode(cmd64.encode("utf-8")).decode("utf-8")
        self.show("Received command:", cmd)
        fuzzy = zoe.Fuzzy()
        analysis = fuzzy.analyze(cmd)
        self.show("Command analysis:", analysis)
        stripped = analysis["stripped"]
        canonical, score = fuzzy.lookup(stripped, self._commands)
        if score < NaturalAgent.likelihood:
            print("I don't understand", parser)
        else:
            self.docommand(parser, analysis, canonical)    

    def docommand(self, parser, analysis, canonical):
        stripped = analysis["stripped"]
        params = self.shellParams(analysis)
        cmdproc, cmdparams = self._commands[canonical]
        shellcmd = [cmdproc, " ".join(cmdparams),
                    "--run",  
                    "--stripped",  "'" + stripped + "'", 
                    "--original",  "'" + analysis["original"] + "'", 
                    "--canonical", "'" + canonical + "'"]
        shellcmd.append(params)
        for key in parser._map:
            for value in parser.list(key):
                if key[0:10] == "attachment":
                    value = self.savefile(value)
                shellcmd.append("--msg-" + key)
                shellcmd.append("'" + value + "'")
        shellcmd = " ".join(shellcmd)
        print("Executing:\n", shellcmd.replace("--", "\n    --"))
        p = subprocess.Popen(shellcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        totalfeedback = []
        for line in p.stdout.readlines():
            line = line.decode("utf-8")#.strip()
            print("cmdproc: ", line)
            if line[:8] == "message ":
                print("Sending back to the server", line[8:])
                self._listener.sendbus(line[8:])
            if line[:9] == "feedback ":
                print("Sending feedback", line[9:])
                totalfeedback.append(line[9:])
        if totalfeedback:
            message = "".join(totalfeedback)
            self.feedback(parser, message)

    def savefile(self, value):
        f = tempfile.NamedTemporaryFile(delete = False)
        f.write(value.encode('utf-8'))
        f.close()
        print("file saved", f.name)
        return f.name
            
    def feedback(self, original, text):
        aMap = {"dst":original.get("src"), 
                "src":"natural", 
                "tag":"command-feedback", 
                "feedback-string":text}
        m = zoe.MessageBuilder.override(original, aMap)
        self._listener.sendbus(m.msg())
            
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
                    params = params + "--" + key + " '" + value + "' "
            else:
                params = params + "--" + key + " '" + value + "' "
        return params
