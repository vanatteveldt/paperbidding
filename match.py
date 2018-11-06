import os
from collections import defaultdict

from django.db.models import Q

from similarity import Similarity

os.environ["DJANGO_SETTINGS_MODULE"] = "paperbidding.settings"
import django

django.setup()

from unidecode import unidecode
from bidding.models import Paper, Author, Authorship, Bid
import csv

reference = defaultdict(str)  # {email: texts}
reviewers = []  # [{id, email}]
alias = {}  # name: email


def clean(x):
    return unidecode(x.lower().strip())


def _name(fn, ln):
    fn = clean(fn.split(" ")[0])
    ln = clean(ln.split(" ")[-1])
    return ", ".join([ln, fn])


def add_reference(email, *texts):
    email = email.lower().strip()
    reference[email] = "\n\n".join([reference[email]] + list(texts) )


# read 2018 abstracts (for reference)
for line in csv.DictReader(open("data/2018_abstracts.csv")):
    title = line['Title']
    abstract = line['Abstract']
    authors = line['Authors'].split(";")
    emails = line['Author Emails'].split(",")
    for email, name in zip(emails, authors):
        add_reference(email, title, abstract)
        # add name: email for matching unknowns
        name = name.split(",")[0].strip()
        fn = name.split(" ")[0]
        ln = name.split(" ")[-1]
        alias[_name(fn, ln)] = email

for paper in Paper.objects.all():
    for a in paper.authorship_set.all():
        add_reference(a.author.email, paper.title, paper.abstract)

print("Loading word vectors")
sim = Similarity()
print("Computing matches")
for reviewer in Author.objects.filter(Q(volunteer=True) | Q(first_author=True)):
    print(reviewer)
    email = reviewer.email
    if email in reference:
        reftext = reference[email]
    else:
        name = _name(reviewer.first_name, reviewer.last_name)
        if name not in alias:
            # cannot do matching :-(
            continue
        reftext = reference[alias[name]]

    for paper in Paper.objects.all():
        text = "\n\n".join([paper.title, paper.abstract])
        s = sim.similarity(text, reftext)
        Bid.objects.create(paper=paper, author=reviewer, score=1, weight=s)


    #print(reviewer, reviewer.email in reference)