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
import poplib
import threading
import time
import traceback
import tempfile
import subprocess
import os

class MailFeedback:
    def __init__(self, to, m):
        self._to = to
        self._m = m

    def feedback(self, msg):
        self._m.text(msg)
    
    def send(self):
        self._m.sendto(self._to)

class MailAgent:
    def __init__(self, smtp, smtpport, user, password, pop3, pop3port, enable_dkim, interval = 5):
        self._listener = zoe.Listener(self, name = "mail")
        self._smtp = smtp
        self._smtpport = smtpport
        self._user = user
        self._password = password
        self._pop3 = pop3
        self._pop3port = pop3port
        self._interval = interval
        self._enable_dkim = enable_dkim == "true"

    def start(self):
        if (self._interval > 0):
            self._fetchThread = threading.Thread (target = self.fetch)
            self._fetchThread.start()
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        if "received" in parser.tags():
            self.rcvmail(parser)
        elif "command-feedback" in parser.tags():
            self.feedback(parser)
        else:
            self.sendmail(parser)

    def rcvmail(self, parser):
        b64 = parser.get("body")
        text = base64.standard_b64decode(b64.encode("utf-8")).decode("utf-8")
        mail = email.message_from_string(text)
        rcpt = mail["From"]
        sender = self.finduser(rcpt)
        if not sender:
            self._listener.log("mail", "debug", "Received a mail from an unknown address " + mail["from"])
            return
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
    
    def finduser(self, address):
        name, addr = email.utils.parseaddr(address)
        model = zoe.Users()
        subjects = model.subjects()
        for s in subjects:
            if "mail" in subjects[s] and subjects[s]["mail"] == addr:
                return subjects[s]

    def guess(self, rcpt):
        if "@" in rcpt:
            return rcpt
        return zoe.Users().subject(rcpt)["mail"]

    def sendmail(self, parser):
        recipient = self.guess(parser.get("to"))
        s = parser.get("subject")
        txt = parser.get("txt")
        txt64 = parser.list("txt64")
        files = parser.list("file")
        atts = parser.list("att")
        htmls = parser.list("html")
        self._listener.log("mail", "debug", "email to " + recipient + " requested", parser)
        m = zoe.Mail(self._smtp, self._smtpport, self._user, self._password)
        if s:
            m.subject(s)
        if txt:
            m.text(txt)
        if files:
            for f in files:
                m.file(f)
        if atts:
            for att in atts:
                a = zoe.Attachment.build(att)
                mime = a.mime()
                b64 = a.base64()
                filename = a.filename()
                m.base64(b64, mime, filename)
        if htmls:
            for html in htmls:
                a = zoe.Attachment.build(html)
                h = a.plaintext() 
                m.html(h)
        if txt64:
            for t in txt64:
                a = zoe.Attachment.build(t)
                h = a.plaintext() 
                m.text(h)
        m.sendto(recipient) 
        self._listener.log("mail", "info", "email sent to " + recipient, parser)

    def feedback(self, parser):
        recipient = self.guess(parser.get("sender"))
        sender = self.finduser(recipient)
        if not sender:
            self._listener.log("mail", "debug", "Received a mail from an unknown address " + recipient)
            return
        txt = parser.get("feedback-string")
        mid = parser.get("inreplyto")
        m = zoe.Mail(self._smtp, self._smtpport, self._user, self._password)
        m.text(txt)
        m.inreplyto(mid)
        m.sendto(recipient)
        self._listener.log("mail", "info", "email sent to " + recipient, parser)

    def savefile(self, value):
        f = tempfile.NamedTemporaryFile(delete = False)
        f.write(value)
        f.close()
        return f.name
   
    def check_rcpt(self, mailcontents):
        mailbytes = b'\n'.join(mailcontents) + b'\n'
        mail = email.message_from_bytes(mailbytes)
        rcpt = mail["From"]
        sender = self.finduser(rcpt)
        return sender

    def check_dkim(self, mailcontents):
        if not self._enable_dkim:
            return True
        mailbytes = b'\r\n'.join(mailcontents) + b'\r\n'
        fname = self.savefile(mailbytes)
        command = "cat " + fname + " | opendkim-testmsg"
        retcode = subprocess.call(command, shell=True)
        return retcode == 0
 
    def receive_mail(self, mailcontents):
        sender = self.check_rcpt(mailcontents)
        if not sender:
            print("Invalid sender")
            self._listener.log("mail", "debug", "Received a mail from an unknown address " + mail["from"])
            return
        dkim = self.check_dkim(mailcontents)
        if not dkim:
            print("Invalid DKIM")
            self._listener.log("mail", "debug", "Received a mail with invalid DKIM signature")
            return
        print("Valid mail")
        self.mailproc(mailcontents)

    def mailproc(self, mailcontents):
        mailbytes = b'\n'.join(mailcontents) + b'\n'
        fname = self.savefile(mailbytes)
        mailproc = os.environ["ZOE_HOME"] + "/mailproc"
        procs = [mailproc + "/" + f for f in os.listdir(mailproc)]
        procs = [p for p in procs if os.access(p, os.X_OK)]
        for proc in procs:
            p = subprocess.Popen(proc + " " + fname, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout.readlines():
                line = line.decode("utf-8")
                if line[:8] == "message ":
                    print("Sending back to the server", line[8:])
                    self._listener.sendbus(line[8:])
    
    def fetch(self):
        while True:
            try:
                print("Fetching mail from", self._pop3)
                conn = poplib.POP3_SSL(self._pop3, self._pop3port)
                conn.user(self._user)
                conn.pass_(self._password)
                messages = conn.list()[1]
                count = len(messages)
                print("Fetched", count, "messages")
                mails = []
                for i in range(count):
                    message = conn.retr(i + 1)[1]
                    mails.append(message)
                conn.quit()
                print("Executing...")
                for mail in mails:
                    self.receive_mail(mail)
                print("done!")
            except Exception as e:
                traceback.print_exc()
            time.sleep(60 * self._interval)

