import django

django.setup()

from bidding.models import Bid
import csv, sys
w = csv.writer(sys.stdout)
w.writerow(["author", "email", "paper", "title", "score"])
authors = {}
for bid in Bid.objects.exclude(score=0):
    w.writerow([bid.author.id, bid.author.email, bid.paper.id, bib.paper.title, bid.score])