import argparse
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

def send_mail(msg, email, pwd):
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


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--email', help='Limit to this email address')
parser.add_argument('--password', help='Email password (will print to screen if not given')
parser.add_argument('--ignore', help='List of email addresses to ignore')
args = parser.parse_args()


if args.ignore:
    ignore ={line.split()[0] for line in open(args.ignore)}
    print(f"** Ignoring {len(ignore)} authors from {args.ignore}")
else:
    ignore = {}

if (not args.email) and (not args.password):
    print("Please specify --email and/or --password!\n\n")
    parser.print_usage()
    sys.exit(1)

if args.email:
    authors = [Author.objects.get(email=args.email)]
else:
    authors = Author.objects.filter(Q(first_author=True) | Q(volunteer=True))

TEMPLATE = open("email_invitation.txt").read()
for author in authors:
    if author.email in ignore:
        continue
    code = get_hash(author.email)
    url = f'http://bid.ica-cm.org/?email={author.email}&code={code}'
    msg = TEMPLATE.format(name = author.first_name, url=url)
    if args.password:
        print(author.email)
        send_mail(msg, author.email, args.password)
    else:
        print(msg)
