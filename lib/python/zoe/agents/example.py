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

# This is the Example Agent
# Launch it with a script like:
#
# import zoe
# agent = zoe.ExampleAgent()
# agent.start()
#
# This agent expects a message with a person's name and email address, and
# sends him a hello email
#
# The input message will be:
# dst=example & name=John Doe & email=john@doe.com
#
# The output message will be:
# dst=mail & to=john@doe.com & subject=Hello from Zoe & txt=Hi, John Doe
#
# Any message with dst=example will be redirected to this agent.
# Don't forget to register the agent in the configuration file zoe.conf:
#
# [agent example]
# port: [whatever]
#
class ExampleAgent:
    def __init__(self):
        """ The constructor. You are free to use your own superclass
            and constructor parameters
        """
        self._listener = zoe.Listener(self, name = "example")

    def start(self):
        """ Starts the agent. Called from the startup script
        """
        self._listener.start()

    def stop(self):
        """ Stops the agent.
        """
        self._listener.stop()

    def receive(self, parser):
        """ Called from self._listener when a message arrives.
            The message is represented by the parser.
            Messages are key-value pairs:
            key1 -> value1
            key2 -> value2.1, value2.2, value2.3

            The parser works as follows:
            parser.get("...") -> returns the value for the given key, which can be a string or a list of strings
            parser.get("key1") -> "value1"
            parser.get("key2") -> ["value2.1", "value2.2", "value2.3"]
            parser.list("...") -> return the value for the given key as a list, whatever its real class is
            parser.list("key1") -> ["value1"]
            parser.list("key2") -> ["value2.1", "value2.2", "value2.3"]

        """
        # read input parameters
        name = parser.get("name")
        email = parser.get("email")
        
        # create a new message
        # we could create it with a plain old string:
        msg = "dst=mail&to=%s&subject=Hello from Zoe&txt=Hi, %s" % (email, name)
        
        # but for long messages it is more convenient to generate it from a map:
        aMap = {"dst"    :"mail", 
                "to"     :email, 
                "subject":"Hello from Zoe", 
                "txt"    :"Hi, " + name}
        msg = zoe.MessageBuilder(aMap).msg()

        # send back the new message
        self._listener.sendbus(msg)

        # we are done!
