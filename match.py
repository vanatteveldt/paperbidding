import argparse
import os
import sys
from collections import defaultdict
from pathlib import Path

from django.db.models import Q

from similarity import Similarity, clean

os.environ["DJANGO_SETTINGS_MODULE"] = "paperbidding.settings"
import django

django.setup()

from bidding.models import Paper, Author, Authorship, Bid
import csv

reference = defaultdict(list)  # {email: texts}
reviewers = []  # [{id, email}]
alias = {}  # name: email

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('abstracts_files', nargs="+", type=Path, help='File containing the CM abstracts for this year')
parser.add_argument('--embeddings_file', nargs="?", type=Path, help='File containing the CM volunteers for this year',
                    default=Path("data/GoogleNews-vectors-negative300-SLIM.bin"))
args = parser.parse_args()

if Paper.objects.count() == 0:
    print("No papers found to match against! Please run import.py before running mathch.py")
    sys.exit(1)

print("** Loading reference texts")
for file in args.abstracts_files:
    n = 0
    with file.open() as f:
        for line in csv.DictReader(f):
            id = int(line['\ufeffCONTROL ID'])
            abstract = line['ABSTRACT BODY']
            title = line['TITLE']
            email = line['AUTHORS (ADDRESS & EMAIL) (E-mail)']
            #Note: These files are one author per line, so no need to split email address
            reference[email].append("\n\n".join([title, abstract]))
            n += 1
    print(f"*** Added {n} reference texts from {file}")

n = 0
for paper in Paper.objects.all():
    for a in paper.authorship_set.all():
        n += 1
        reference[a.author.email].append("\n\n".join([paper.title, paper.abstract, *paper.keywords.split("|")]))
print(f"*** Added {n} reference texts from this year's papers")

n = 0
for a in Author.objects.all():
    if a.keywords.strip():
        n += 1
        reference[a.email].append(" ".join(a.keywords.split("|")))
print(f"*** Added {n} reference texts from volunteer keywords")

vector_file = args.embeddings_file or Path("data/")
print(f"** Loading word vectors from {args.embeddings_file}")
sim = Similarity(model_file=args.embeddings_file)
print(f"*** Loaded {sim.num_words} word vectors with dimensionality {sim.num_features}")

print("** Computing matches")
n = 0
n_unknown = 0
for reviewer in Author.objects.filter(Q(volunteer=True) | Q(first_author=True)):
    if Bid.objects.filter(author=reviewer).exists():
        continue
    email = reviewer.email
    try:
        reftexts = reference[email]
    except KeyError:
        print(f"##### No reference text found for {reviewer.email} ({reviewer.first_name} {reviewer.last_name})")
        n_unknown += 1
        continue

    for paper in Paper.objects.all():
        text = "\n\n".join([paper.title, paper.abstract])
        s = sim.similarity(text, "\n\n".join(reftexts))
        Bid.objects.create(paper=paper, author=reviewer, score=-1, weight=s)
    n += 1
print(f"*** Assigned similarity scores for {n} reviewers (skipped {n_unknown} reviewers)")

    #print(reviewer, reviewer.email in reference)