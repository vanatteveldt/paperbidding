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
    
Thanks for volunteering to review for the Computational Methods group!

We are excited to introduce a new paper bidding process this year, which hopefully will help us match reviewers better with papers they are interested in reviewing.  
    
If you already bid on papers because you are also a paper submitter, please ignore this mail.
        
You can go to the following URL to bid for at least 10 papers you are willing to review (we will try to assign at most 2 or 3 papers per reviewer):

{url}
    
  
Please complete the bidding survey as soon as possible, but before November 14th (next Tuesday!). 
We will assign all papers for review by November 15th. All reviews should be due by December 1st. 
    
As always, this is a tight schedule, but since we will only be assigning a small amount of papers/abstracts we are confident that it should not be too much of a burden. 
    
Happy bidding!
    
Cindy Shen (vice-chair) 
Wouter van Atteveldt (chair)

PS: This is the first time we're doing this and we had to write the paper bidding site ourself, so please mail us if you spot any bugs or have other feedback!
""".format(**locals())
    #email = 'vanatteveldt@gmail.com'
    smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login('vanatteveldt@gmail.com', pwd)

    fromaddr = 'wouter@vanatteveldt.com'
    sub = '[urgent] ICA-CM Paper bidding'

    msg = MIMEText(msg)
    msg['From'] = fromaddr
    msg['To'] = email
    msg['Subject'] = sub

    smtpserver.sendmail(fromaddr, email, msg.as_string())

#sent = {line.split()[0] for line in open('sent.txt')}
pwd = sys.argv[1]

for author in Author.objects.filter(submitter=False):#.filter(email='m.wettstein@ipmz.uzh.ch'):
 #   if author.email in sent:
 #       continue
    code = get_hash(author.email)
    url = 'http://bid.ica-cm.org/?email={author.email}&code={code}'.format(**locals())
    print(author.email, url)
    send_mail(author.email, author.first_name, url, pwd)
