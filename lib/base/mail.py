#-*- encoding:utf-8 -*-
'''
Created on 2013-12-22 21:23:37
Update on 2015-05-21
@author: qiujingqin
'''
import os
import types
import datetime
import time
import mimetypes
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from optparse import OptionParser
import sys
import re

class GMT8(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=8)
    def dst(self, dt):
        return datetime.timedelta(hours=8)
    def tzname(self, dt):
        return "GMT+8"

class ADatetime():
    def __init__(self, days = 0, hours=0, minutes=0, seconds=0):
        '''
        time offset here 
        include days, hours, minutes, seconds
        '''
        self.reset(days=days, hours=hours, minutes=minutes, seconds=seconds)

    def reset(self, days = 0, hours=0, minutes=0, seconds=0):
        self._days = days
        self._hours = hours
        self._minutes = minutes
        self._seconds = seconds
        self._dt = datetime.datetime.now(GMT8()) - datetime.timedelta(days=self._days,hours=self._hours, minutes=self._minutes,seconds=self._seconds)
        return self

    def get_datetime(self):
        return self._dt.strftime("%Y-%m-%d %H:%M:%S")

class Mail(object):
    
    def __init__(self,username,password,smtp_server,port=25, mtype="plain"):
        self._username = username
        self._password = password
        self._smtp_server = smtp_server
        self._port = port
        self._mtype = mtype
        
    def send_mail(self, mfrom, tolist, subject, content, mtype=None, attachment=None):
        assert type(tolist) == types.ListType
        m_type = mtype if mtype else self._mtype
        try:
                m_content = "\
                %s \
                \n\n\
                -------------------------------------------------------------------------\n\
                From OPS! Auto send @%s, please don't reply! \n\
                "  % (content, ADatetime().get_datetime())
                
                if m_type == "html":
                        m_content = m_content.replace("\n", "<br />")
                
                m_charset = "utf-8"
                
                msg = MIMEMultipart()
                msg['Subject']= subject   #email title
                msg['From']=mfrom   #sender
                msg['To']=','.join(tolist)  #recipient
                msg['date']=time.strftime('%a, %d %b %Y %H:%M:%S %z')  #define send datetime
                
                ## text
                text = MIMEText(m_content, _subtype=m_type, _charset=m_charset)
                msg.attach(text)
                
                ## attachment
                if(attachment and os.path.exists(attachment)):
                    ctype,encoding = mimetypes.guess_type(attachment)
                    if ctype is None or encoding is not None:
                        ctype = 'application/octet-stream'
                    maintype,subtype = ctype.split('/',1)  
                    
                    with open(attachment, 'rb') as fh:
                        file_content = fh.read()
                        att = MIMEImage(file_content,subtype)
                        att["Content-Disposition"] = 'attachmemt;filename="%s"' % attachment
                        msg.attach(att)
                 
                smtp=smtplib.SMTP()
                smtp.connect(self._smtp_server, port=self._port)  #smtp server,
                #username password to login stmp server
                smtp.ehlo()
                smtp.starttls()
                smtp.login(self._username , self._password)
                smtp.sendmail(mfrom , tolist , msg.as_string())
                smtp.quit()
                return True
        except Exception,data:
                import traceback
                tb = traceback.format_exc()
                print str(tb)
                return False
            
    def send_html_mail(self, mfrom, tolist, subject, content, attachment=None):
        self.send_mail(mfrom, tolist, subject, content, mtype="html", attachment=attachment)

if __name__ == "__main__":
    
    EMAIL_SENDER="opsnotice@fangdd.com"
    EMAIL_LOGIN_NAME="opsnotice@fangdd.com"
    EMAIL_LOGIN_PASSWD="A8ikj0cD2"
    EMAIL_SERVER="smtp.exmail.qq.com"
    EMAIL_SERVER_PORT = 25

    parser = OptionParser()  
    parser.add_option("-s", "--subject", dest="subject", default=None,
                      action="store", help="the subject of this email", metavar="SUBJECT")  
    parser.add_option("-b", "--body",  
                      action="store", dest="body", default=None,  
                      help="the body of this email", metavar="BODY")
    parser.add_option("-t", "--to",  
                      action="store", dest="to", default=None,  
                      help="who(s) can recevice this email", metavar="TOLIST")
    parser.add_option("-f", "--format",  
                      action="store", dest="format", default=None,  
                      help="plain or html", metavar="FORMAT")
    parser.add_option("-a", "--attachment",  
                      action="store", dest="attachment", default=None,  
                      help="attachment file", metavar="ATTACHMENT")
    
    (options, args) = parser.parse_args()

    
    (subject, body, tolist, fmt, attachment) = (options.subject, options.body, options.to, options.format, options.attachment)
    
    mail = Mail(EMAIL_LOGIN_NAME, EMAIL_LOGIN_PASSWD, EMAIL_SERVER, EMAIL_SERVER_PORT)
    
    if subject and body and tolist:
        tolist = re.split("[,; ]", tolist)
        if fmt == 'html':
            mail.send_html_mail(EMAIL_SENDER, tolist, subject, body, attachment=attachment)
        else:
            mail.send_mail(EMAIL_SENDER, tolist, subject, body, attachment=attachment)
    else:
        print "Usage:\n\tpython %s -h" % (sys.argv[0])
    