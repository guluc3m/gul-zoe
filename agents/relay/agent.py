#!/usr/bin/env python3
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
from zoe.deco import *

@Agent("relay")
class RelayAgent:

    @Message(tags = ["relay"])
    def receive(self, parser):
        print("Received", parser)
        builder = zoe.MessageBuilder.fromparser(parser)
        builder = builder.put("relayto", None)
        builder = builder.put("dst", parser.get("relayto"))
        builder = self.fillsender(parser, builder)
        print("  builder:", builder)
        return builder       
 
    def fillsender(self, parser, builder):
        sender = parser.get("sender")
        if not sender: 
            return builder
        user = zoe.Users().subject(sender)
        if not user: 
            return builder
        for key in user:
            builder = builder.put("sender-" + key, user[key])
        return builder

