"""
Send review invitations to all reviewers. Run this after match.py
"""

import argparse
import os

import django
from django.db.models import Q
from bidding.views import get_hash
from bidding.models import Author, Paper
from mail import send_mail

os.environ["DJANGO_SETTINGS_MODULE"] = "paperbidding.settings"
django.setup()

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--email', help='Limit to this email address')
parser.add_argument('--password', help='Email password (will print to screen if not given')
parser.add_argument('--ignore', help='List of email addresses to ignore')
parser.add_argument('--check', help='Check only, do not send', action="store_true")
args = parser.parse_args()


if args.ignore:
    ignore ={line.split()[0] for line in open(args.ignore)}
    print(f"** Ignoring {len(ignore)} authors from {args.ignore}")
else:
    ignore = {}

if (not args.email) and (not args.password) and (not args.check):
    print("# Note: No password given, checking only!")
    args.check = True

if args.email:
    authors = [Author.objects.get(email=args.email)]
else:
    authors = list(Author.objects.filter(Q(first_author=True) | Q(volunteer=True)))

print(f"** Sending out email to {len(authors)} reviewers (including {len(ignore)} that will be ignored)")

TEMPLATE = open("email_invitation.txt").read()
for author in authors:
    if author.email in ignore:
        continue
    code = get_hash(author.email)
    url = f'http://bid.ica-cm.org/?email={author.email}&code={code}'
    msg = TEMPLATE.format(name = author.first_name, url=url)
    if args.check:
        print(author.email, url)
    elif args.password:
        print(author.email)
        send_mail(msg, "ICA-CM Paper Bidding", author.email, args.password)
    else:
        print(msg)
