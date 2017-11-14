# assign papers based on bids
# constraints: all papers 3 reviewers, papers spread evenly over reviewers
# optimize: give people the paper they want
# naive attempt: pick paper with lowest # of bids, assign to reviewers with lowest # of bids
import csv

import sys

from collections import defaultdict

c, reviewers, papers, solution = defaultdict(set), defaultdict(set), defaultdict(set), defaultdict(set)

for row in csv.DictReader(sys.stdin):
    if row['score'] == "1":
        r, p = row['email'], row['paper']
        reviewers[r].add(p)
        papers[p].add(r)
        c[r].add(p)

def argmin(x, func):
    result, value = None, None
    for e in x:
        v = func(e)
        if value is None or v < value:
            result, value = e, v
    return result

while papers:
    p = argmin(papers, lambda p: len(papers[p]))
    candidates = papers[p] - {r for (r,p) in solution.items() if len(p) >= 3}
    for r in [1,2,3]:
        if not candidates:
            print("NO CANDIDATES FOR ", p)
            break
        r = argmin(candidates, lambda r: len(reviewers[r]))
        candidates.remove(r)
        reviewers[r].remove(p)
        solution[r].add(p)
    del papers[p]

w = csv.writer(sys.stdout)
#w.writerow(["paper", "reviewer"])

for r, p in solution.items():
    print(len(p), r, p, c[r], all(x in c[r] for x in p))