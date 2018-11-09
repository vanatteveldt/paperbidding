import os
os.environ["DJANGO_SETTINGS_MODULE"] = "paperbidding.settings"
import django

django.setup()

import smtplib

import django;
from email.mime.text import MIMEText

django.setup()
from bidding.views import get_hash

from bidding.models import Author
from django.db.models import Q

def send_mail(email, name, url, pwd):
    msg = """
Dear {name},

You are receiving this email because you submitted a paper to the computational methods interest group and/or volunteered to review for us. Thanks very much for your interest and support!

This year, CM again is using a paper bidding process, which we successfully implemented last year. This process aims to help us match reviewers better with papers they are interested in reviewing.  

Please go to the following URL to bid for at least 10 papers you are willing to review (we will try to assign 2 or 3 papers per reviewer). It only takes one minute to bid. 

{url}

As noted in the CfP, we expect every author to also function as a reviewer. This ensures that the burden of reviewing is shared evenly and allows us to only assign a limited amount of papers to each reviewer. If you are really unable to review about 3 papers/abstracts, please email us as soon as possible with the name and email address of one of your co-authors or colleagues that is able to participate in the review process. 

Please complete the bidding survey *before Saturday November 10th*, midnight (Hawaii). We hope to assign all papers for review by November 11th. All reviews should be due by December 1st. As always, this is a short period of time, but since we will only be assigning a small amount of papers/abstracts we are confident that it should not be too much of a burden. 

Happy bidding!

Cindy and Wouter
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

sent = {line.split()[0] for line in open('sent.txt')}
print(sent)
pwd = sys.argv[1]

#authors = Author.objects.filter(email__in=['cuishen@ucdavis.edu', 'wouter@vanatteveldt.com'])
#authors = Author.objects.filter(email__in=['wouter@vanatteveldt.com'])
authors = Author.objects.filter(Q(volunteer=True) | Q(first_author=True))
print(len(list(authors)))

for author in authors:
    if author.email in sent:
        continue
    code = get_hash(author.email)
    url = 'http://bid.ica-cm.org/?email={author.email}&code={code}'.format(**locals())
    print(author.email, url)
    send_mail(author.email, author.first_name, url, pwd)
