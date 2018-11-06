import os

os.environ["DJANGO_SETTINGS_MODULE"] = "paperbidding.settings"
import django

django.setup()

from bidding.models import Paper, Author, Authorship
import csv

# read 2019 volunteers
for line in csv.DictReader(open('data/2019_volunteers.csv')):
    id = line['\ufeff"PERSON (ID)"']
    email = line['PERSON (EMAIL)']
    fn = line['PERSON (FIRST NAME)']
    ln = line['PERSON (LAST NAME)']
    Author.objects.create(scholar_id=id, email=email, first_name=fn, last_name=ln, volunteer=True)

# read 2019 abstracts
for line in csv.DictReader(open('data/2019_abstracts.csv')):
    email = line['AUTHORS (ADDRESS & EMAIL) (E-mail)'].lower().strip()
    id = int(line['CONTROL ID'])
    contact = line['CONTACT (NAME ONLY)']
    title = line['TITLE']
    abstract = line['ABSTRACT BODY: Abstract Body (Individual Submission)']
    fn = line["AUTHORS (ADDRESS & EMAIL) (First name)"]
    ln = line["AUTHORS (ADDRESS & EMAIL) (Last name)"]

    try:
        a = Author.objects.get(email=email)
        if not a.submitter:
            a.submitter = True
            a.save()
    except Author.DoesNotExist:
        a = Author.objects.create(email=email, first_name=fn, last_name=ln, submitter=True)

    try:
        p = Paper.objects.get(pk=id)
    except Paper.DoesNotExist:
        p = Paper.objects.create(id=id, title=title, abstract=abstract)

    try:
        Authorship.objects.get(author=a, paper=p)
    except Authorship.DoesNotExist:
        n = len(p.authorship_set.all()) + 1
        Authorship.objects.create(author=a, paper=p, number=n)
        if n == 1 and not a.first_author:
            a.first_author = True
            a.save()
