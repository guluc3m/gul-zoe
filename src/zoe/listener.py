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

import sys
import uuid
import socket
import threading
import traceback
from zoe.zp import *

RESET = '\033[0m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'

class Listener:
    def __init__(self, host, port, delegate, serverhost, serverport, debugmode = False, timeout = None):
        self._host, self._port = host, port
        self._srvhost, self._srvport = serverhost, serverport
        self._delegate = delegate
        self._running = False
        self._debugmode = debugmode
        self._timeout = timeout

    def start(self, sockethook = None):
        self._running = True
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self._host, self._port))
        (self._host, self._port) = self._socket.getsockname()
        self._socket.listen(10)
        if sockethook:
            sockethook()
        self._socket.settimeout(1)
        while self._running:
            try:
                if self._timeout and self._timeout > 0:
                    self._timeout = self._timeout - 1
                    if self._timeout < 1:
                        return
                conn, addr = self._socket.accept()
                thread = threading.Thread(target = self.connection, args = (conn, addr))
                thread.start()
            except Exception as e:
                pass

    def mylog(self, colour, header, host, port, message):
        if self._debugmode:
            print (colour + header + " " + host + ":" + str(port) + " " + message + RESET)

    def log(self, source, level, msg, original = None):
        aMap = {"dst":"log", "src":source, "lvl":level, "msg":msg}
        m = MessageBuilder(aMap, original).msg()
        self.sendbus(m)

    def connection(self, conn, addr):
        message = ""
        host, port = addr
        while True:
            data = conn.recv(1024)
            if not data: break
            message = message + data.decode("utf-8")
        conn.close()
        self.mylog (YELLOW, "RECV", host, port, message)
        parser = MessageParser(message)
        tags = parser.tags()
        if "exit!" in tags:
            self.stop()
            return
        try:
            self._delegate.receive(parser)
        except:
            print("EXCEPTION")
            traceback.print_exc()
            print("FLUSH")
            sys.stdout.flush()
            sys.stderr.flush()

    def stop(self):
        self._running = False
        self._socket.close()

    def send(self, message, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, port))
            s.sendall(message.encode("utf-8"))
            self.mylog (GREEN, "SENT", host, port, message)
        except Exception as e:
            self.mylog (RED, "ERR ", host, port, message)
            #raise e
        finally:
            s.close()

    def sendbus(self, message):
        self.send(message, self._srvhost, self._srvport)

