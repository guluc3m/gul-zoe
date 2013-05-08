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
import getopt

def usage():
    print ("Usage: python3.2 " + sys.argv[0] + " [options]")
    print ("    Options:")
    print ("        --help         Shows this help")
    print ("        -s, --src      Source of the message to intercept")
    print ("        -t, --topic    Topic to listen for the message")
    print ("        -m, --msg      Message to send")

argv = sys.argv[1:]
source = None
msg = None
topic = None

try:
    opts, args = getopt.getopt(argv, "hs:t:m:", ["help", "src=", "topic=", "msg="])
except Exception as e:
    usage()
    sys.exit(1)

for opt, arg in opts:
    if opt in ("-s", "--src"):
        source = arg
    if opt in ("-m", "--msg"):
        msg = arg
    if opt in ("-t", "--topic"):
        topic = arg
    if opt in ("-h", "--help"):
        usage()
        sys.exit(0)

if not source or not msg or not topic:
    usage()
    sys.exit(2)

def show(parser):
    keys = list(parser._map.keys())
    keys.sort()
    for key in keys:
        print (key + "=" + str(parser.get(key)))

def callback(parser):
    agent.stop()
    show(parser)
    sys.exit(0)

agent = zoe.StalkerAgent("localhost", 0, "localhost", 30000, (source, topic, msg), callback)
agent.start()

