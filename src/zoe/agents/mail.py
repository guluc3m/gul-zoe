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
import base64
import uuid
import re
import email

class MailFeedback:
    def __init__(self, to, m):
        self._to = to
        self._m = m

    def feedback(self, msg):
        self._m.text(msg)
        self._m.sendto(self._to)

class MailAgent:
    def __init__(self, host, port, serverhost, serverport, smtp, smtpport, user, password):
        self._listener = zoe.Listener(host, port, self, serverhost, serverport, True)
        self._smtp = smtp
        self._smtpport = smtpport
        self._user = user
        self._password = password

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        if "received" in parser.tags():
            self.rcvmail(parser)
        else:
            self.sendmail(parser)

    def rcvmail(self, parser):
        b64 = parser.get("body")
        text = base64.standard_b64decode(b64.encode("utf-8")).decode("utf-8")
        mail = email.message_from_string(text)
        mp = mail.is_multipart()
        if not mp:
            parts = [ mail ]
        else:
            parts = mail.get_payload()
        for part in parts:
            mime = part.get_content_type()
            if not mime == "text/plain":
                continue
            text = part.get_payload()
            s = text.find("\n\n")
            command = text[:s].strip()
            bigstring = text[s:].strip()
            f = zoe.Fuzzy()
            context = {}
            rcpt = mail["From"]
            subject = mail["Subject"]
            context["bigstring"] = bigstring
            context["sender"] = rcpt
            context["feedback"] = MailFeedback(rcpt, zoe.Mail(self._smtp, self._smtpport, self._user, self._password).subject(subject))
            r = f.execute(command, context)

    def sendmail(self, parser):
        recipient = parser.get("to")
        s = parser.get("subject")
        txt = parser.get("txt")
        txt64 = parser.get("txt64")
        files = parser.get("file")
        atts = parser.get("att")
        htmls = parser.get("html")
        self._listener.log("mail", "debug", "email to " + recipient + " requested", parser)
        m = zoe.Mail(self._smtp, self._smtpport, self._user, self._password)
        if s:
            m.subject(s)
        if txt:
            m.text(txt)
        if files:
            if files.__class__ is str:
                files = [files]
            for f in files:
                m.file(f)
        if atts:
            if atts.__class__ is str:
                atts = [atts]
            for att in atts:
                a = zoe.Attachment.build(att)
                mime = a.mime()
                b64 = a.base64()
                filename = a.filename()
                m.base64(b64, mime, filename)
        if htmls:
            if htmls.__class__ is str:
                htmls = [htmls]
            for html in htmls:
                a = zoe.Attachment.build(html)
                h = a.plaintext() 
                m.html(h)
        if txt64:
            if txt64.__class__ is str:
                txt64 = [txt64]
            for t in txt64:
                a = zoe.Attachment.build(t)
                h = a.plaintext() 
                m.text(h)
        m.sendto(recipient) 
        self._listener.log("mail", "info", "email sent to " + recipient, parser)
