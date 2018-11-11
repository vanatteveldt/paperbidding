import os;
from collections import defaultdict
os.environ["DJANGO_SETTINGS_MODULE"] = "paperbidding.settings"
import django; django.setup()
from bidding.models import Bid, Paper
import csv, sys
all_bids = defaultdict(set)

papertypes = {} # paper_id: type
for line in csv.DictReader(open("2019_abstracts2.csv")):
    papertypes[int(line['\ufeffControl ID'])] = line['Presentation Type'].split()[-1]

for b in Bid.objects.exclude(score=-1).exclude(score=-99).select_related("author", "paper").defer("paper__abstract"):
    if "shen@ucd" in b.author.email:
        continue
    b.paper.ptype = papertypes[b.paper_id]
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
        if b.paper.ptype == "Paper":
            fullpapers[b.author] = fullpapers.get(b.author, 0) + 1
        solution[b.author].add(b)
        n = ", ".join([b.author.last_name, b.author.first_name])
        w.writerow([b.paper.id, b.paper.ptype, b.paper.title, b.author.scholar_id, b.author.email, n, b.score, b.weight])

#for a, bids in solution.items():
#    if len(bids) != 2:
#        print(a, len(bids))
##    if fullpapers[a] > 2:
#        print(a)
