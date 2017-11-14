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

As you might know, we are experimenting with some changes to the review process.
This means that all submitters are expected to review as well, and reviewers can
choose which papers to review themselves in a process known as 'paper bidding'.

Although if our administration is correct you did not submit to CM this year 
(or not as first author), you are of course more than welcome to participate 
in the review process.

We only just got the list of member emails, so unfortunately the time table is 
really tight: we will need your bid by tomorrow night.  Of course, we totally 
understand if this does not work for you, and you are in no way obliged to 
participate, but if you see one or two interesting papers feel free to select them!

To do the paper bidding, please visit the link below:

{url}

We will assign all papers for review by November 15th. All reviews should be due 
by December 1st. 
    
As always, this is a tight schedule, but since we will only be assigning a small 
amount of papers/abstracts we are confident that it should not be too much of a burden. 
    
Happy bidding!
    
Cindy Shen (vice-chair) 
Wouter van Atteveldt (chair)

PS This is the first time we're doing this and we had to write the paper bidding site
ourself, so please mail us if you spot any bugs or have other feedback!
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

sent = {line.split()[0] for line in open('sent.txt')} | {"lorraine.borghetti@gmail.com"}
pwd = sys.argv[1]

for author in Author.objects.filter(submitter=False, volunteer=False):
    code = get_hash(author.email)
    if author.email not in sent:
        url = 'http://bid.ica-cm.org/?email={author.email}&code={code}'.format(**locals())
        print(author.email, url)
        send_mail(author.email, author.first_name, url, pwd)
