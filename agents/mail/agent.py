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

from zoe.deco import *

SMTP = os.environ['zoe_mail_smtp']
SMTPPORT = os.environ['zoe_mail_smtp_port']
POP3 = os.environ['zoe_mail_pop3']
POP3PORT = os.environ['zoe_mail_pop3_port']
USER = os.environ['zoe_mail_user']
PASSWORD = os.environ['zoe_mail_password']
DKIM = os.environ['zoe_mail_enable_dkim']

@Agent("mail")
class MailAgent:
    
    #
    # Receiving mails
    #

    @Timed(60)
    def fetch(self):
        """
        Fetches all the incoming email and starts its processing
        """
        try:
            print("Fetching mail from", POP3)
            conn = poplib.POP3_SSL(POP3, POP3PORT)
            conn.user(USER)
            conn.pass_(PASSWORD)
            messages = conn.list()[1]
            count = len(messages)
            print("Fetched", count, "messages")
            mails = []
            for i in range(count):
                message = conn.retr(i + 1)[1]
                mails.append(message)
            conn.quit()
            print("Executing...")
            rets = []
            for mail in mails:
                ret = self.receive_mail(mail)
                if ret:
                    rets.extend(ret)
            print("done!")
            return rets
        except Exception as e:
            traceback.print_exc()

    def receive_mail(self, mailcontents):
        """
        Starts the processing of an incoming email
        mailcontents -- the email contents as a list of bytes
        """
        mailbytes = b'\n'.join(mailcontents) + b'\n'
        mailobj = email.message_from_bytes(mailbytes)
        sender = self.valid_sender(mailobj)
        if not sender:
            print("Invalid sender")
            return
        dkim = self.check_dkim(mailcontents)
        if not dkim:
            print("Invalid DKIM")
            return
        print("Valid mail")
        return self.mailproc(mailbytes, sender)
    
    def valid_sender(self, mail):
        """
        Returns the Zoe user that corresponds to an email sender, or None if no user is found
        mail -- The email obect as a Message object given by the email lib
        """
        rcpt = mail["From"]
        sender = self.finduser(rcpt)
        return sender

    def check_dkim(self, mailcontents):
        """
        Checks the DKIM signature, returning true if it is correct
        """
        if DKIM != "true":
            return True
        mailbytes = b'\r\n'.join(mailcontents) + b'\r\n'
        fname = self.savefile(mailbytes)
        command = "cat " + fname + " | opendkim-testmsg"
        retcode = subprocess.call(command, shell=True)
        return retcode == 0

    def finduser(self, address):
        """
        Finds the Zoe user with a given email address
        """
        name, addr = email.utils.parseaddr(address)
        model = zoe.Users()
        subjects = model.subjects()
        for s in subjects:
            if "mail" in subjects[s] and subjects[s]["mail"] == addr:
                return subjects[s]
    #
    # mailproc scripts
    #

    def quote(self, s):
        return "'" + s.replace("'", "\\'") + "'"
    
    def parsemail(self, bs, sender):
        params = []
        message = email.message_from_bytes(bs)
        headers = ["subject",
                   "delivered-to",
                   "in-reply-to",
                   "date",
                   "message-id",
                   "from",
                   "to",
                   "reply-to",
                   "list-id",
                   "sender"]
    
        for h in headers:
            if h in message:
                params.append("--mail-" + h)
                params.append(self.quote(message[h]))
   
        params.append("--msg-sender=" + self.quote(sender["uniqueid"]))
        for key in sender:
            params.append("--msg-sender-" + key + "=" + self.quote(sender[key]))

        plain = b""
        for part in message.walk():
            if part.is_multipart(): continue;
            mime = part.get_content_type()
            payload = part.get_payload(decode = True)
            if mime[:5] == "text/":
                charset = part.get_content_charset()
                if charset:
                    payload = payload.decode(charset).encode("utf-8")
            params.append("--" + mime)
            fname = self.savefile(payload)
            params.append(fname)
            if mime == "text/plain":
                plain = plain + payload

        if len(plain) > 0:
            params.append("--plain")
            fname = self.savefile(plain)
            params.append(fname)
            
        return params
    
    def mailproc(self, mailbytes, sender):
        fname = self.savefile(mailbytes)
        params = self.parsemail(mailbytes, sender)
        mailprocdir = os.environ["ZOE_HOME"] + "/mailproc"
        procs = [mailprocdir + "/" + f for f in os.listdir(mailprocdir)]
        procs = [p for p in procs if os.access(p, os.X_OK)]
        rets = []
        for proc in procs:
            print("Executing proc", proc, "over file", fname)
            cmd = [proc, "--original", fname]
            cmd.extend(params)
            cmdline = " ".join(cmd)
            print(cmdline)
            p = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout.readlines():
                print("This proc returned:", line)
                line = line.decode("utf-8")
                if line[:8] == "message ":
                    ret = line[8:].strip()
                    rets.append(ret)
                    print("Sending back to the server", ret)
        return rets

    def savefile(self, value):
        f = tempfile.NamedTemporaryFile(delete = False)
        f.write(value)
        f.close()
        return f.name

    #
    # Sending emails
    #

    def guess(self, rcpt):
        if "@" in rcpt:
            return rcpt
        return zoe.Users().subject(rcpt)["mail"]

    @Message(tags = [])
    def sendmail(self, parser):
        recipient = self.guess(parser.get("to"))
        s = parser.get("subject")
        txt = parser.get("txt")
        txt64 = parser.list("txt64")
        files = parser.list("file")
        atts = parser.list("att")
        htmls = parser.list("html")
        self.logger.debug("email to " + recipient + " requested")
        m = zoe.Mail(SMTP, SMTPPORT, USER, PASSWORD)
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
        self.logger.info("email sent to " + recipient)

    @Message(tags = ["command-feedback"])
    def feedback(self, parser):
        recipient = self.guess(parser.get("sender"))
        sender = self.finduser(recipient)
        if not sender:
            self._listener.log("mail", "debug", "Received a mail from an unknown address " + recipient)
            return
        txt = parser.get("feedback-string")
        mid = parser.get("inreplyto")
        m = zoe.Mail(SMTP, SMTPPORT, USER, PASSWORD)
        m.text(txt)
        m.inreplyto(mid)
        m.sendto(recipient)
        self.logger.info("email sent to " + recipient)

