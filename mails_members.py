import os

from django.db.models import Q

os.environ["DJANGO_SETTINGS_MODULE"] = "paperbidding.settings"
import django

django.setup()


import csv, sys
import smtplib

import django;
import email
from email.mime.text import MIMEText

django.setup()
from bidding.views import get_hash

from bidding.models import Author, Paper

#for author in Author.objects.all():
#    print(author.email, )


def send_mail(email, name, url, pwd):
    msg = """
Dear {name},

First of all, thanks for being part of the Computational Methods interest group.

You are receiving this email because you volunteered to review for the 
Computational Methods group, or you submitted as first author to us, in which case we expect 
you to review as well.

As a reviewer, you can indicate which papers to review themselves in a process known as 'paper bidding'.

We only just got the list of submissions, so unfortunately the time table is 
really tight: we will need your bid by Friday night (!). 

To do the paper bidding, please visit the link below:

{url}

We will assign all papers for review by November 15th. All reviews should be due 
by December 1st. 
    
As always, this is a tight schedule, but since we will only be assigning a small 
amount of papers/abstracts we are confident that it should not be too much of a burden. 
    
Happy bidding!
    
Cindy Shen (vice-chair) 
Wouter van Atteveldt (chair)

PS As always, please mail us if you spot any bugs or have other feedback!
""".format(**locals())
    #email = 'vanatteveldt@gmail.com'
    smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login('vanatteveldt@gmail.com', pwd)

    fromaddr = 'wouter@vanatteveldt.com'
    sub = 'ICA-CM Paper bidding'

    msg = MIMEText(msg)
    msg['From'] = fromaddr
    msg['To'] = email
    msg['Subject'] = sub

    smtpserver.sendmail(fromaddr, email, msg.as_string())

sent = {}#{line.split()[0] for line in open('sent.txt')} | {"lorraine.borghetti@gmail.com"}
pwd = sys.argv[1]

for author in Author.objects.filter(Q(first_author=True) | Q(volunteer=True)):
    code = get_hash(author.email)
    if author.email != "wouter@vanatteveldt.com":
        continue
    if author.email not in sent:
        url = 'http://bid.ica-cm.org/?email={author.email}&code={code}'.format(**locals())
        print(author.email, url)
        #send_mail(author.email, author.first_name, url, pwd)
