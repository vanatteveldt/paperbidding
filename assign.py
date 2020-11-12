"""
Assign reviewers to papers based on their bids. This is the final script in the workflow

The assignment uses a greedy algorithm that (IIUC) goes through all papers,
starting with the one with the least bids on it.
Then it sorts the bidders for that paper starting with the people that have the least assignments so far,
where full papers count more than abstracts
(in case of ties it favours the best match according to the matching step).
Then, it simply assigns the first three reviewers and goes to the next paper.

It will give an error message if any paper had less than three bids.
For now it ignores 'no' and 'conflict', but since we have always been able to assign papers to 'yes' bidders,
that doesn't seem to be a problem.
"""


import os;
from collections import defaultdict
os.environ["DJANGO_SETTINGS_MODULE"] = "paperbidding.settings"
import django; django.setup()
from bidding.models import Bid, Paper
import csv, sys
all_bids = defaultdict(set)

for b in Bid.objects.exclude(score=-1).exclude(score=-99).select_related("author", "paper").defer("paper__abstract"):
    all_bids[b.paper].add(b)

assert len(all_bids) == Paper.objects.count()

solution = defaultdict(set) # author: bid
fullpapers = defaultdict(int) # author: n_full_papers
w = csv.writer(sys.stdout)
w.writerow(["paper_id", "type", "title", "author_id", "email", "name", "score", "weight"])

# hack: give these people extra papers, they deserve it :)
boost = {} # email : boostpoints

for paper, bids in sorted(all_bids.items(), key=lambda pa: len(pa[1])):
    bids = [b for b in bids if len(solution[b.author]) < 3]
    bids = sorted(bids, key=lambda b: (-boost.get(b.author.email, 0), -b.score, fullpapers.get(b.author, 0)*.5 + len(solution[b.author]), -b.weight if b.weight else 0))
    if len(bids) < 3:
        raise Exception("Fewer than 3 reviewers left for paper!")
    for b in bids[:3]:
        if boost.get(b.author.email, 0) > 0:
            boost[b.author.email] -= 1
        if b.paper.type == "Paper":
            fullpapers[b.author] = fullpapers.get(b.author, 0) + 1
        solution[b.author].add(b)
        n = ", ".join([b.author.last_name, b.author.first_name])
        w.writerow([b.paper.id, b.paper.type, b.paper.title, b.author.scholar_id, b.author.email, n, b.score, b.weight])
