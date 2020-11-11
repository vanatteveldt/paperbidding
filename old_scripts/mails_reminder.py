import os


os.environ["DJANGO_SETTINGS_MODULE"] = "paperbidding.settings"
import django

django.setup()
from django.db.models import Q

import csv, sys
import smtplib

import django;
import email
from email.mime.text import MIMEText

django.setup()
from bidding.views import get_hash

from bidding.models import Author, Paper, Bid


#for author in Author.objects.all():
#    print(author.email, )


def send_mail(email, name, url, pwd):
    msg = """
Dear {name},
    
First of all, thanks for submitting to or volunteering for Computational Methods!

As you know, all authors who submit to CM are expected to also review, and we use a paper bidding system to 
allow you to  pick papers you are interested in to review.

Unfortunately, ICA reviews work on a very tight time table, so we really need your bid by tomorrow night (!). 

Can you please take 5 minutes to go over the list of papers and mark at least 10 papers that you would be 
interested in reviewing? 

Link: {url}

(If you already bid and I messed up the filter, sorry! You can just ignore this mail.) 

So far, more than 100 people already bid on papers. If everyone chips in, we can be sure that no one 
will have to review more than 2 or 3 abstracts or papers. The papers are sorted by relevance based on similarity 
to your submission(s), so hopefully the most interesting papers will be near the top.

If you are really unwilling or unable to review, please send us an email, preferably with the name of a 
co-author or someone else who can take over.  

We will (try to) assign all papers for review by November 12th. All reviews should be due by December 1st. 
    
As always, this is a tight schedule, but since we will only be assigning a small amount of papers/abstracts 
we are confident that it should not be too much of a burden. 
    
Happy bidding!
    
Cindy Shen (vice-chair) 
Wouter van Atteveldt (chair)
""".format(**locals())
    #email = 'vanatteveldt@gmail.com'
    smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login('vanatteveldt@gmail.com', pwd)

    fromaddr = 'wouter@vanatteveldt.com'
    sub = '[urgent] Reminder: ICA-CM Paper bidding'

    msg = MIMEText(msg)
    msg['From'] = fromaddr
    msg['To'] = email
    msg['Subject'] = sub

    smtpserver.sendmail(fromaddr, email, msg.as_string())

done = set(Bid.objects.exclude(score=-1).values_list("author_id", flat=True))
print(len(done))
authors = Author.objects.filter(Q(volunteer=True) | Q(first_author=True)).exclude(pk__in=done)
#authors = authors.filter(email='wouter@vanatteveldt.com')
#print(len(authors))
pwd = sys.argv[1]
seen = []#{b["email"] for b in csv.DictReader(sys.stdin)}
for author in authors:
    code = get_hash(author.email)
    url = 'http://bid.ica-cm.org/?email={author.email}&code={code}'.format(**locals())
    if author.email not in seen:
        print(author.email, url)
        send_mail(author.email, author.first_name, url, pwd)
        #break
