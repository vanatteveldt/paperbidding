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

keywords = {} # id : keywords

for line in csv.DictReader(open('data/2019_abstracts2.csv')):
    id = int(line['\ufeffControl ID'])
    title = line['Title']
    kws = line['Keywords'].strip()
    kwset = set()
    if kws != "none":
        for kw in kws.split(";"):
            if kw.strip():
                k = kw.replace("- Computational Methods", "").strip()
                if k not in kwset:
                    kwset.add(k)
    keywords[id] = kwset

for line in csv.DictReader(open('data/2019_all_submissions.csv')):
    id = int(line['\ufeffCONTROL ID'])

    if id not in keywords:
        continue # let's ignore submissions outside CM

    abstract = line['ABSTRACT BODY']
    title = line['TITLE']
    email = line['AUTHORS (ADDRESS & EMAIL) (E-mail)']
    add_reference(email, title, abstract, *keywords[id])

for paper in Paper.objects.all():
    for a in paper.authorship_set.all():
        add_reference(a.author.email, paper.title, paper.abstract, *paper.keywords.split("|"))

for a in Author.objects.all():
    add_reference(a.email, *a.keywords.split("|"))

print("Loading word vectors")
sim = Similarity()
print("Computing matches")

for reviewer in Author.objects.filter(Q(volunteer=True) | Q(first_author=True)):
    if Bid.objects.filter(author=reviewer).exists():
        continue
    print(reviewer)
    email = reviewer.email
    if email in reference:
        reftext = reference[email]
    else:
        name = _name(reviewer.first_name, reviewer.last_name)
        if name not in alias:
            print("no match :-(")
            # cannot do matching :-(
            continue
        reftext = reference[alias[name]]

    for paper in Paper.objects.all():
        text = "\n\n".join([paper.title, paper.abstract])
        s = sim.similarity(text, reftext)
        Bid.objects.create(paper=paper, author=reviewer, score=-1, weight=s)


    #print(reviewer, reviewer.email in reference)