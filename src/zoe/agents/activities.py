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
import zoe
import threading
import datetime
import tenjin
import time
import json
import base64
import uuid
from tenjin.helpers import *

class ActivitiesAgent:
    def __init__(self):
        self._listener = zoe.Listener(self, name = "activities")
        self._users = None
        self._banking = None
        self._inventory = None
        self._courses = None
        self._lists = None

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        tags = parser.tags()
        if "memo" in tags:
            if "json" in tags:
                self.json(parser)
            else:
                self.memo(parser)
        if "users" in tags and "notification" in tags:
            self.updateUsers(parser)
        if "banking" in tags and "notification" in tags:
            self.updateBanking(parser)
        if "inventory" in tags and "notification" in tags:
            self.updateInventory(parser)
        if "courses" in tags and "notification" in tags:
            self.updateCourses(parser)
        if "lists" in tags and "notification" in tags:
            self.updateLists(parser)
        #self._listener.sendbus(response)

    def updateUsers(self, parser):
        presi = parser.get(parser.get("group-junta-presi") + "-name")
        vice = parser.get(parser.get("group-junta-vice") + "-name")
        coord = parser.get(parser.get("group-junta-coord") + "-name")
        tesorero = parser.get(parser.get("group-junta-tesorero") + "-name")
        vocal = parser.get(parser.get("group-junta-vocal") + "-name")
        self._users = {"presi":presi, "vice":vice, "tesorero":tesorero, "coord":coord, "vocal":vocal}
        self._listener.log("activities", "info", "Users info received", parser)

    def updateBanking(self, parser):
        ids = parser.list("ids")
        if len(ids) == 0:
            self._listener.log("activities", "WARNING", "Banking info empty!", parser)
        incomings = []
        expenses = []
        for id in ids:
            date = parser.get(id + "-date")
            amount = parser.get(id + "-amount")
            what = parser.get(id + "-what")
            m = (date, amount, what)
            if float(amount) > 0:
                incomings.append(m)
            else:
                expenses.append(m)
        incomings = sorted(incomings, key = lambda i: i[0])
        expenses = sorted(expenses, key = lambda i: i[0])
        balance = parser.get("balance")
        self._banking = (incomings, expenses, balance)
        self._listener.log("activities", "info", "Banking info received", parser)
    
    def updateInventory(self, parser):
        ids = parser.list("ids")
        if len(ids) == 0:
            self._listener.log("activities", "WARNING", "Inventory info empty!", parser)
        objects = []
        for id in ids:
            amount = parser.get(id + "-amount")
            what = parser.get(id + "-what")
            o = (amount, what)
            objects.append(o)
        self._inventory = objects
        self._listener.log("activities", "info", "Inventory info received", parser)

    def updateCourses(self, parser):
        courseids = parser.get("courseids")
        if not courseids:
            self._courses = None
            self._listener.log("activities", "ERROR", "Courses info empty!", parser)
            return
        if courseids.__class__ is str:
            courseids = [courseids]
        courses = []
        for id in courseids:
            mindate = parser.get("course-" + id + "-mindate")
            maxdate = parser.get("course-" + id + "-maxdate")
            lectids = parser.get("course-" + id + "-lectureids")
            lectures = []
            for lid in lectids:
                title = parser.get("course-" + id + "-lecture-" + lid)
                lectures.append(title)
            c = (mindate, maxdate, lectures)
            courses.append(c)
        courses = sorted(courses, key = lambda c: c[0])
        self._courses = courses
        self._listener.log("activities", "info", "Courses info received", parser)

    def updateLists(self, parser):
        inlist = len(parser.get("list-gul-members"))
        inbook = parser.get("book-members")
        self._lists = (inlist, inbook)
    
    def requestUsers(self, original):
        msg = zoe.MessageBuilder({"dst":"users","tag":"notify"}, original).msg()
        self._listener.sendbus(msg)
        self._listener.log("activities", "info", "Users request sent", original)
    
    def requestBanking(self, original):
        courseyear = zoe.Courses.courseyears()
        msg = zoe.MessageBuilder({"dst":"banking","tag":"notify", "year":courseyear}, original).msg()
        self._listener.sendbus(msg)
        self._listener.log("activities", "info", "Banking request sent for year " + courseyear, original)
    
    def requestInventory(self, original):
        msg = zoe.MessageBuilder({"dst":"inventory","tag":"notify"}, original).msg()
        self._listener.sendbus(msg)
        self._listener.log("activities", "info", "Inventory request sent", original)
    
    def requestCourses(self, original):
        courseyear = zoe.Courses.courseyears()
        msg = zoe.MessageBuilder({"dst":"courses","tag":"notify", "year":courseyear}, original).msg()
        self._listener.sendbus(msg)
        self._listener.log("activities", "info", "Courses request sent for year " + courseyear, original)
    
    def requestLists(self, original):
        msg = zoe.MessageBuilder({"dst":"lists","tag":"notify"}, original).msg()
        self._listener.sendbus(msg)
        self._listener.log("activities", "info", "Lists request sent", original)

    def prerequisites(self, original, retry = True):
        print ("Checking prerequisites")
        print ("  Checking user list")
        success = True
        if self._users == None:
            print ("    missing")
            self.requestUsers(original)
            success = False

        print ("  Checking accounting")
        if self._banking == None:
            print ("    missing")
            self.requestBanking(original)
            success = False
        
        print ("  Checking inventory")
        if self._inventory == None:
            print ("    missing")
            self.requestInventory(original)
            success = False
        
        print ("  Checking courses")
        if self._courses == None:
            print ("    missing")
            self.requestCourses(original)
            success = False

        print ("  Checking lists")
        if self._lists == None:
            print ("    missing")
            self.requestLists(original)
            success = False

        if success:
            return True

        if retry:
            print ("Prerequisites not met. Let me try again in a few seconds...")
            time.sleep(10)
            return self.prerequisites(original, False)
        else:
            print("Prerequisites not met, please check the logs and try again");
            return False

    def memodata(self, original):
        if not self.prerequisites(original):
            return
        courseyear = zoe.Courses.courseyears()
        (incomings, expenses, balance) = self._banking
        (inlist, inbook) = self._lists
        data = {
            "CURSO"         :courseyear,
            "ALTAS_EN_LISTA":inlist,
            "ALTAS_EN_LIBRO":inbook,
            "PRESIDENTE"    :self._users["presi"],
            "VICEPRESIDENTE":self._users["vice"], 
            "COORDINADOR"   :self._users["coord"],
            "TESORERO"      :self._users["tesorero"],
            "VOCAL"         :self._users["vocal"], 
            "INVENTARIO"    :self._inventory,
            "CURSOS"        :self._courses,
            "INGRESOS"      :incomings,
            "GASTOS"        :expenses, 
            "SALDO"         :balance,
        }
        return data
  
    def json(self, original):
        self._listener.log("activities", "debug", "JSON memo requested", original)
        data = self.memodata(original)
        if not data:
            return
        j = json.dumps(data, indent=2, ensure_ascii=False)
        b64 = base64.standard_b64encode(j.encode('utf-8')).decode('utf-8')
        attachment = zoe.Attachment(b64, "application/json", "memoria.json")
        aMap = {"src":"activities", "topic":"activities", "tag":["generated-memo", "json"], "memo":attachment.str()}
        msg = zoe.MessageBuilder(aMap, original).msg()
        self._listener.sendbus(msg)
        self._listener.log("activities", "info", "JSON memo generated", original)
        self.send_if_requested(original, attachment)

    def memo(self, original):
        self._listener.log("activities", "debug", "PDF memo requested", original)
        data = self.memodata(original)
        if not data:
            return
        engine = tenjin.Engine()
        out = engine.render('activities_memo.tex', data)
        if original.get("_cid"):
            cid = original.get("_cid")
        else:
            cid = str(uuid.uuid4())
        filename = cid + ".tex"
        here = os.getcwd()
        os.chdir("/tmp")
        f = open(filename, "w")
        f.write(out)
        f.close()
        os.system("pdflatex " + filename)
        os.system("pdflatex " + filename)
        filename = cid + ".pdf"
        f = open(filename, 'rb')
        data = f.read()
        f.close()
        os.chdir(here)
        b64 = base64.standard_b64encode(data).decode('utf-8')
        attachment = zoe.Attachment(b64, "application/pdf", "memoria.pdf")
        aMap = {"src":"activities", "topic":"activities", "tag":["generated-memo", "pdf"], "memo":attachment.str()}
        msg = zoe.MessageBuilder(aMap, original).msg()
        self._listener.sendbus(msg)
        self._listener.log("activities", "info", "PDF memo generated", original)
        self.send_if_requested(original, attachment)
        
    def send_if_requested(self, parser, attachment):
        recipient = parser.get("mail")
        if not recipient:
            return
        aMap = {"src":"activities", "dst":"mail", "to":recipient, "subject":"Memoria de actividades", "att":attachment.str()}
        msg = zoe.MessageBuilder(aMap, parser).msg()
        self._listener.sendbus(msg)
        self._listener.log("activities", "info", "HTML memo mailed to " + recipient, parser)
