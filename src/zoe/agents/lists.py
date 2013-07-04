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
import time
import base64
import threading

class ListsAgent:
    def __init__(self, interval = 10):
        self._listener = zoe.Listener(self, name = "lists")
        self._model = zoe.Lists()
        self._interval = interval
        self.update()

    def start(self):
        if (self._interval > 0):
            self._resendDaemonThread = threading.Thread (target = self.loop)
            self._resendDaemonThread.start()
        self._listener.start(self.notify)

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        tags = parser.tags()
        if "notify" in tags:
            self.notify(parser)
        if "set" in tags:
            self.setmembers(parser)

    def notify(self, original = None):
        members = self._model.members()
        aMap = {"src":"lists", "topic":"lists", "tag":["lists", "notification"], "book-members":str(members)}
        listnames = []
        lists = self._model.lists()
        for l in lists:
            listnames.append(l)
            aMap["list-" + l + "-members"] = lists[l] 
        aMap["lists"] = listnames
        m = zoe.MessageBuilder(aMap, original).msg()
        self._listener.sendbus(m)
        ingul = len(lists["gul"])
        self._listener.log("lists", "info", "Lists info notified: " + str(ingul) + " in GUL and " + str(members) + " members")

    def update(self):
        self._listener.log("lists", "debug", "Updating lists info")
        oldmodel = self._model
        self._model = zoe.Lists()
        self.postupdate(oldmodel, self._model)

    def postupdate(self, old, new):
        oldmembers = set(old.list("gul"))
        currentmembers = set(new.list("gul"))
        gone = oldmembers - currentmembers
        new = currentmembers - oldmembers
        self._listener.log("lists", "info", "new members in GUL: " + str(new))
        self._listener.log("lists", "info", "members gone away from GUL: " + str(gone))
        self.welcome(list(new))
        self.farewell(list(gone))

    def mail(self, addr, subject, text):
        b64 = base64.standard_b64encode(text.encode('utf-8')).decode('utf-8')
        attachment = zoe.Attachment(b64, "text/plain", "hello.txt")
        aMap = {"dst":"mail", "to":addr, "subject":subject, "txt64":attachment.str()}
        msg = zoe.MessageBuilder(aMap).msg()
        return msg

    def welcome(self, members):
        for addr in members:
            # OK this is temporary, some templates should be written
            # and stored as files, in the spirit of reminders.sh
            text = """
Hola, %s

Te doy la bienvenida a la lista del GUL UC3M. Aquí podrás hablar 
con personas con intereses sobre Linux y software libre, plantear 
tus dudas y participar en los debates y flames que de vez en cuando se 
organizan.

Actualmente hay %d personas apuntadas a la lista, así que recuerda
tener un trato agradable y respetuoso. Excepto con los programadores
de Ruby. Puedes meterte con ellos todo lo que quieras.

Permíteme recordarte que el GUL es una organización sin ánimo de 
lucro, por lo que no te remitiremos publicidad ni cederemos tus 
datos a nadie. 

Si te apetece, este es un buen momento para presentarte enviando 
un email a gul@gul.uc3m.es y contando un poco sobre ti. 

Espero que tu experiencia en el GUL sea satisfactoria. 

Recibe un saludo, 

Zoe
"""
            msg = self.mail(addr, "Te doy la bienvenida a la lista del GUL UC3M", text % (addr, len(self._model.list("gul"))))
            self._listener.sendbus(msg)
    
    def farewell(self, members):
        for addr in members:
            # OK this is temporary, some templates should be written
            # and stored as files, in the spirit of reminders.sh
            text = """
Hola, %s

Tu baja de la lista del GUL UC3M se ha tramitado correctamente.
Espero que tu estancia aquí haya sido satisfactoria.

Vuelve pronto, 

Zoe
"""
            msg = self.mail(addr, "Baja de la lista del GUL UC3M", text % (addr))
            self._listener.sendbus(msg)

    def setmembers(self, parser):
        self._listener.log("lists", "debug", "Updating members info")
        inbook = parser.get("inbook")
        self._model.setmembers(inbook)
        self._listener.log("lists", "info", "Members info updated to " + inbook)
        self.notify(parser)

    def loop(self):
        while True:
            time.sleep(self._interval)
            self.update()
            self.notify()
