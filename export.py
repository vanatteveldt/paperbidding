import django

django.setup()

from bidding.models import Bid
import csv, sys
w = csv.writer(sys.stdout)
w.writerow(["author", "mtype", "email", "paper", "title", "score"])
authors = {}
for bid in Bid.objects.exclude(score=0):
    mtype = "submitter" if bid.author.submitter else ("volunteer" if bid.author.volunteer else "member")
    w.writerow([bid.author.id, mtype, bid.author.email, bid.paper.id, bid.paper.title.encode("utf-8"), bid.score])
