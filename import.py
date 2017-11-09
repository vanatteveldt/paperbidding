import csv, sys
import django; django.setup()
from bidding.models import Author, Paper

papers = list(csv.DictReader(sys.stdin))

for paper in papers:
    try:
        author = Author.objects.get(email=paper["Email Address"])
    except Author.DoesNotExist:
        print("Creating")
        author = Author.objects.create(id=paper['Member Number'], email=paper["Email Address"], first_name=paper['First Name'], middle_name=paper['Middle Name'], last_name=paper['Last Name'], affiliation=paper['Affiliation'])

    Paper.objects.create(id=paper['All Academic Code'], type=paper['Individual Submission Type'], title=paper['Title'], abstract=paper['Abstract'], first_author=author, author_emails=paper['Author Emails'])
