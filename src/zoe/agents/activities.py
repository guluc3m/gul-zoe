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
import threading
import datetime
import tenjin
from tenjin.helpers import *

class ActivitiesAgent:
    def __init__(self, host, port, serverhost, serverport):
        self._listener = zoe.Listener(host, port, self, serverhost, serverport)
        self._users = None
        self._banking = None
        self._inventory = None
        self._courses = None

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        tags = parser.tags()
        if "memo" in tags:
            self.memo()
        if "users" in tags and "notification" in tags:
            self.updateUsers(parser)
        if "banking" in tags and "notification" in tags:
            self.updateBanking(parser)
        if "inventory" in tags and "notification" in tags:
            self.updateInventory(parser)
        if "courses" in tags and "notification" in tags:
            self.updateCourses(parser)
        #self._listener.sendbus(response)

    def updateUsers(self, parser):
        presi = parser.get(parser.get("group-junta-presi") + "-name")
        vice = parser.get(parser.get("group-junta-vice") + "-name")
        coord = parser.get(parser.get("group-junta-coord") + "-name")
        tesorero = parser.get(parser.get("group-junta-tesorero") + "-name")
        vocal = parser.get(parser.get("group-junta-vocal") + "-name")
        self._users = {"presi":presi, "vice":vice, "tesorero":tesorero, "coord":coord, "vocal":vocal}

    def updateBanking(self, parser):
        ids = parser.get("ids")
        if ids.__class__ is str:
            ids = [ids]
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
    
    def updateInventory(self, parser):
        ids = parser.get("ids")
        if ids.__class__ is str:
            ids = [ids]
        objects = []
        for id in ids:
            amount = parser.get(id + "-amount")
            what = parser.get(id + "-what")
            o = (amount, what)
            objects.append(o)
        self._inventory = objects

    def updateCourses(self, parser):
        courseids = parser.get("courseids")
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

    def requestUsers(self):
        msg = zoe.MessageBuilder({"dst":"users","tag":"notify"}).msg()
        self._listener.sendbus(msg)
    
    def requestBanking(self):
        courseyear = zoe.Courses.courseyears()
        msg = zoe.MessageBuilder({"dst":"banking","tag":"notify", "year":courseyear}).msg()
        self._listener.sendbus(msg)
    
    def requestInventory(self):
        msg = zoe.MessageBuilder({"dst":"inventory","tag":"notify"}).msg()
        self._listener.sendbus(msg)
    
    def requestCourses(self):
        courseyear = zoe.Courses.courseyears()
        msg = zoe.MessageBuilder({"dst":"courses","tag":"notify", "year":courseyear}).msg()
        self._listener.sendbus(msg)

    def memo(self):
        print ("Checking prerequisites")
        print ("  Checking user list")
        success = True
        if not self._users:
            print ("    missing")
            self.requestUsers()
            success = False

        print ("  Checking accounting")
        if not self._banking:
            print ("    missing")
            self.requestBanking()
            success = False
        
        print ("  Checking inventory")
        if not self._inventory:
            print ("    missing")
            self.requestInventory()
            success = False
        
        print ("  Checking courses")
        if not self._courses:
            print ("    missing")
            self.requestCourses()
            success = False

        # blah
        if not success:
            print ("Prerequisites not met. Please try again")
            return

        # Please use a template here.
        courseyear = zoe.Courses.courseyears()
        (incomings, expenses, balance) = self._banking
        
        data = {
            "CURSO"         :courseyear,
            "ALTAS_EN_LISTA":444, # TODO 
            "ALTAS_EN_LIBRO":90,  # TODO
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
    
        engine = tenjin.Engine()
        out = engine.render('activities_memo.tex', data)
        print(out)
