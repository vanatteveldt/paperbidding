import csv, sys
import django; django.setup()
from bidding.models import Author, Paper, Bid

for row in csv.DictReader(sys.stdin):
    author = Author.objects.get(email=row['author'])
    paper = Paper.objects.get(id=int(row['paper']))
    weight = float(row['agg.weight'])

    try:
        b = Bid.objects.get(author=author, paper=paper)
        b.weight = weight
        b.save()
    except Bid.DoesNotExist:
        Bid.objects.create(author=author, paper=paper, weight=weight, score=0)
