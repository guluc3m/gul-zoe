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

import time
import datetime
import threading
import configparser
import zoe

class CoursesAgent:
    def __init__(self, interval = 60, url = "http://cursos.gul.es/index.php/courses/json"):
        self._listener = zoe.Listener(self, name = "courses")
        self._model = zoe.Courses(url)
        self._interval = interval
        self._url = url

    def update(self):
        self._model.update()
        self._listener.log("courses", "info", "Updating course information from " + self._url)
        self.notify()

    def start(self):
        if (self._interval > 0):
            self._resendDaemonThread = threading.Thread (target = self.loop)
            self._resendDaemonThread.start()
        self._listener.start(self.update())

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        tags = parser.tags()
        if "notify" in tags:
            self.notify(parser)

    def notify(self, original = None):
        if original:
            year = original.get("year")
        else:
            year = zoe.Courses.courseyears()
        courses = self._model.foryear(year)
        aMap = {"src":"courses", "topic":"courses", "tag":["courses", "notification"], "year":str(year)}
        courseids = []
        for course in courses:
            id = course["id"]
            courseids.append(id)
            aMap["course-" + id + "-mindate"] = course["mindate"]
            aMap["course-" + id + "-maxdate"] = course["maxdate"]
            lectureids = []
            for lecture in course["lectures"]:
                lid = lecture["id"]
                lectureids.append(lid)
                aMap["course-" + id + "-lecture-" + lid] = lecture["title"]
            aMap["course-" + id + "-lectureids"] = lectureids
        aMap["courseids"] = courseids
        msg = zoe.MessageBuilder(aMap, original).msg()
        self._listener.sendbus(msg)
        self._listener.log("courses", "info", "Sending courses notification", original)
        
    def loop(self):
        while True:
            time.sleep(self._interval)
            self.update()

