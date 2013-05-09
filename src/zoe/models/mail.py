
import os
import zoe
import smtplib
import mimetypes
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

    def text(self, text):
        self._msg.attach(MIMEText(text))
        return self

    def file(self, path, name = None):
        if not name:
            name = os.path.basename(path)
        ctype, encoding = mimetypes.guess_type(path)
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

    def sendto(self, recipient):
        self._msg['To'] = recipient
        server = smtplib.SMTP(self._smtp, self._port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(self._user, self._password)
        server.sendmail(self._user, recipient, self._msg.as_string())
        server.close()
        return self

