import os
os.environ["DJANGO_SETTINGS_MODULE"] = "paperbidding.settings"
import django

django.setup()

from bidding.models import Paper, Author, Authorship
import csv
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('abstracts_file', type=Path, help='File containing the CM abstracts for this year')
parser.add_argument('volunteers_file', type=Path, help='File containing the CM volunteers for this year')
args = parser.parse_args()

# read volunteers
n = 0
with args.volunteers_file.open() as f:
    for line in csv.DictReader(f):
        id = line['\ufeffPerson ID']
        email = line['Email Address']
        fn = line['First Name']
        ln = line['Last Name']
        try:
            Author.objects.get(scholar_id=id)
            # already exists, so skip
        except Author.DoesNotExist:
            n += 1
            Author.objects.create(scholar_id=id, email=email, first_name=fn, last_name=ln, volunteer=True)
print(f"** Added {n} authors to the database")

# read 2019 abstracts
n_authors = 0
n_new_papers = 0
with args.abstracts_file.open() as f:
    lines = list(csv.DictReader(f))
    for line in lines:
        email = line['AUTHORS (ADDRESS & EMAIL) (E-mail)'].lower().strip()
        id = int(line['\ufeffCONTROL ID'])
        #contact = line['CONTACT (NAME ONLY)']
        title = line['TITLE']
        abstract = line['ABSTRACT BODY']
        fn = line["AUTHORS (ADDRESS & EMAIL) (First name)"]
        ln = line["AUTHORS (ADDRESS & EMAIL) (Last name)"]

        try:
            a = Author.objects.get(email=email)
            if not a.submitter:
                a.submitter = True
                a.save()
        except Author.DoesNotExist:
            a = Author.objects.create(email=email, first_name=fn, last_name=ln, submitter=True)
            n_authors += 1

        try:
            p = Paper.objects.get(pk=id)
        except Paper.DoesNotExist:
            p = Paper.objects.create(id=id, title=title, abstract=abstract)
            n_new_papers += 1

        try:
            Authorship.objects.get(author=a, paper=p)
        except Authorship.DoesNotExist:
            n = len(p.authorship_set.all()) + 1
            Authorship.objects.create(author=a, paper=p, number=n)
            if n == 1 and not a.first_author:
                a.first_author = True
                a.save()
print(f"** Imported {n_new_papers} new papers ({len(lines)} in total) and created {n_authors} new authors that did not volunteer")