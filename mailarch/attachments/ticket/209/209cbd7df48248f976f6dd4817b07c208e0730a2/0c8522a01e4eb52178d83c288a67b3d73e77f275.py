#!/usr/bin/env python

# Based on http://stackoverflow.com/questions/14483195/how-to-handle-asyncore-within-a-class-in-python-without-blocking-anything
# with some modification (wrap_loop) because the above link results in a race on close that exhibits as a 
# bad descriptor exception on a listen that shouldn't be happening. Instead, we make breaking the loop explicit as
# based on http://www.velocityreviews.com/forums/t337756-modification-to-asyncore-py-to-support-threaded-event-loop.html

import smtpd
import datetime
import time
import threading
import asyncore
import smtplib

from email.Utils import make_msgid, formatdate , parseaddr, getaddresses
from email.MIMEText import MIMEText

class AsyncCoreLoopThread(object):

    def wrap_loop(self, exit_condition, timeout=1.0, use_poll=False, map=None):
        if map is None:
            map = asyncore.socket_map
            while map and not exit_condition:
                asyncore.loop(timeout=1.0, use_poll=False, map=map, count=1)

    def start(self):
        """Start the listening service"""
        self.exit_condition = []
        kwargs={'exit_condition':self.exit_condition,'timeout':1.0} 
        self.thread = threading.Thread(target=self.wrap_loop,kwargs=kwargs )
        self.thread.start()     

    def stop(self):
        """Stop the listening service"""
        self.exit_condition.append(True)
        self.thread.join()


class ProofOfConceptChannel(smtpd.SMTPChannel):

    # The smtpd classes were really not designed to be overriden.
    # Note the necessary name munging to get to 'private' variables
    def smtp_RCPT(self, arg):
        if not self._SMTPChannel__mailfrom:
            self.push('503 Error: need MAIL command')
            return
        address = self._SMTPChannel__getaddr('TO:', arg) if arg else None
        if not address:
            self.push('501 Syntax: RCPT TO: <address>')
            return
        if "poison" in address:
           self.push('550 Error: Not touching that')
           return
        self._SMTPChannel__rcpttos.append(address)
        self.push('250 Ok')

class ProofOfConceptServer(smtpd.SMTPServer):

    def __init__(self,localaddr,remoteaddr):
        self.inbox=[]
        smtpd.SMTPServer.__init__(self,localaddr,remoteaddr)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            conn, addr = pair
            channel = ProofOfConceptChannel(self, conn, addr)

    def process_message(self, peer, mailfrom, rcpttos, data):
        self.inbox.append(data)

class TestMailSender(object):

    def send_a_message(self,body):
        msg = MIMEText(body)
        msg['Message-ID'] = make_msgid('testmailsender')
        msg['Date'] = formatdate(time.time(), True)
        msg['From'] = "testmailsender@example.com"
        msg['To'] = "testmailrecipient@example.com"
        msg['Cc'] = "poisoned-address@example.com"
        (fname,frm) = parseaddr(msg.get('From'))
        addrlist = msg.get_all('To') + msg.get_all('Cc',[])
        to = [addr for name,addr in getaddresses(addrlist)]
        client = None
        try:
            client=smtplib.SMTP(timeout=5)
            #client.set_debuglevel(1)
            conn_code, conn_msg = client.connect('127.0.0.1:2025')
            unhandled = client.sendmail(frm, to, msg.as_string())
            if unhandled:
               print "Didn't deliver to",unhandled
        except Exception as e:
            print "Exception while sending",e
        finally:
            if client:
                try:
                    client.quit()
                except smtplib.SMTPServerDisconnected:
                    pass

server = ProofOfConceptServer(('127.0.0.1', 2025), None)
ms=AsyncCoreLoopThread()
sender=TestMailSender()
print "starting up",datetime.datetime.now()
ms.start()
sender.send_a_message("Test 1")
sender.send_a_message("Test 2")
sender.send_a_message("Test 3")
ms.stop()
print "Shut down",datetime.datetime.now()
print "The resulting inbox on the server is"
print server.inbox
