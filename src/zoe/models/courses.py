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

import urllib.request
import json
import math
import datetime

class Courses:

    FIRST_MONTH=9

    def __init__(self, url = "http://cursos.gul.es/index.php/courses/json"):
        self._url = url;
        self._withdate = None
        self._courses = []
        self.update()

    def update(self): 
        url = urllib.request.urlopen(self._url)
        contents = url.read().decode("utf-8")
        rawcourses = json.JSONDecoder().decode(contents)
        courses = {}
        for i in rawcourses:
            lectures = []
            for j in rawcourses[i]:
                l = dict(rawcourses[i][j], id = j)
                if l["date"]:
                    lectures.append(l)
            if len(lectures) < 1:
                continue
            lectures = sorted(lectures, key = lambda lecture: lecture["date"])
            mindate = lectures[0]["date"]
            maxdate = lectures[-1]["date"]
            course = dict(id = i, lectures = lectures, mindate = mindate, maxdate = maxdate)
            courses[i] = course
        self._courses = courses
        self._rawcourses = rawcourses

    def foryear(self, year):
        ret = []
        years = year.split("/")
        year_a, year_b = years[0], years[1]
        for course in self._courses:
            cyear, cmonth, cday = self._courses[course]["mindate"].split("-")
            cmonth = int(cmonth)
            if (int(cmonth) < Courses.FIRST_MONTH and cyear == year_b) or (int(cmonth) > Courses.FIRST_MONTH-1 and cyear == year_a):
                ret.append(self._courses[course])
        return ret

    def courseyears(year = None, month = None):
        if not year:
            year = datetime.date.today().year
        if not month:
            month = datetime.date.today().month

        year = int(year)
        month = int(month)

        if month < Courses.FIRST_MONTH:
            return str(year-1) + "/" + str(year)
        else:
            return str(year) + "/" + str(year+1)

