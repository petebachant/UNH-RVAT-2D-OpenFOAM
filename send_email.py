#!/usr/bin/python
"""
From http://alextrle.blogspot.com/2011/05/how-to-send-sms-message-with-python.html:

To send a text message to a t-mobile number, you would use <number>@tmomail.net. To send a text message to an AT&T number, you would use <number>@mms.att.net.
"""

import smtplib
from email.mime.text import MIMEText
import json

# Dictionary with personal info
pinfo = {"gmun" : "someone",
         "gmpw" : "password"}

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(pinfo["gmun"], pinfo["gmpw"])

msg = MIMEText("The simulation is complete, yo.")
msg["Subject"] = "Simulation finished"
msg["From"] = "Your name here"
msg["To"] = "Your name here"

sendtoname = "Your name here"
sendtoaddress = "you@gmail.com"

server.sendmail(sendtoname, sendtoaddress, msg.as_string()) 
