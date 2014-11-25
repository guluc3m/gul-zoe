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
import smtplib
import mimetypes
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.encoders import encode_base64

class Mail:
    def __init__(self, smtp, port, user, password):
        self._user = user
        self._password = password
        self._msg = MIMEMultipart()
        self._msg["From"] = user
        self._smtp = smtp
        self._port = port

    def subject(self, subject):
        self._msg["Subject"] = subject
        return self
    
    def inreplyto(self, mid):
        self._msg["In-Reply-To"] = mid
        return self

    def text(self, text):
        self._msg.attach(MIMEText(text, _charset = "utf-8"))
        return self
    
    def html(self, text):
        self._msg.attach(MIMEText(text, 'html'))
        return self

    def file(self, path, name = None):
        if not name:
            name = os.path.basename(path)
        print("**************", path)
        ctype, encoding = mimetypes.guess_type(path)
        print("ctype", ctype, "encoding", encoding)
        t1, t2 = ctype.split('/')
        f = open(path, 'rb')
        data = f.read()
        f.close()
        attachment = MIMEBase(t1, t2)
        attachment.set_payload(data)
        encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment', filename=name)
        self._msg.attach(attachment)
        return self

    def base64(self, data, ctype, name = None):
        t1, t2 = ctype.split('/')
        attachment = MIMEBase(t1, t2)
        if data.__class__ is str:
            data = data.encode("utf-8")
        data2 = base64.standard_b64decode(data)
        attachment.set_payload(data2)
        encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment', filename=name)
        self._msg.attach(attachment)
        return self

    def sendto(self, recipient):
        if recipient.find("@") == -1:
            # recipient is a user, not an email address
            user = zoe.Users().subject(recipient)
            if not recipient:
                print("Can't find user", user)
                return
            recipient = user["mail"]
        self._msg['To'] = recipient
        server = smtplib.SMTP(self._smtp, self._port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(self._user, self._password)
        server.sendmail(self._user, recipient, self._msg.as_string().encode('UTF-8'))
        server.close()
        return self
