"""
Send reminder emails to reviewers who haven't put in any bid yet
"""

import argparse
import os

from mail import send_mail

os.environ["DJANGO_SETTINGS_MODULE"] = "paperbidding.settings"
import django
django.setup()
from django.db.models import Q
from bidding.views import get_hash
from bidding.models import Author, Paper, Bid


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--password', help='Email password (will print to screen if not given')
parser.add_argument('--ignore', help='List of email addresses to ignore')
parser.add_argument('--check', help='Check only, do not send', action="store_true")
args = parser.parse_args()

if args.ignore:
    ignore ={line.split()[0] for line in open(args.ignore)}
    print(f"** Ignoring {len(ignore)} authors from {args.ignore}")
else:
    ignore = {}
if (not args.password) and (not args.check):
    print("# Note: No password given, checking only!")
    args.check = True

done = set(Bid.objects.exclude(score=0).values_list("author_id", flat=True))
print(f"** Bids received from {len(done)} reviewers")
authors = list(Author.objects.filter(Q(volunteer=True) | Q(first_author=True)).exclude(pk__in=done))
print(f"** {len(authors)} reviewers still need to bid")

TEMPLATE = open("email_reminder.txt").read()
if not args.check:
    print(f"** Sending reminder emails...")

for author in authors:
    if author.email in ignore:
        continue
    code = get_hash(author.email)
    url = 'http://bid.ica-cm.org/?email={author.email}&code={code}'.format(**locals())
    if args.check:
        print(author.email, url)
    else:
        msg = TEMPLATE.format(name=author.first_name, url=url)
        print(author.email)
        send_mail(msg, "REMINDER: ICA-CM Paper bids due tomorrow noon (EU)", author.email, args.password)

