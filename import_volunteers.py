import csv, sys
import django; django.setup()
from bidding.models import Author, Paper

volunteers = list(csv.DictReader(sys.stdin))

for v in volunteers:
    email = v['Email Address']
    if not Author.objects.filter(email=email).exists():
        print(email)
        Author.objects.create(id=v['Member Number'], email=email,
                              first_name=v['First Name'], middle_name=v['Middle Name'], last_name=v['Last Name'],
                              affiliation=v['Affiliation'], submitter=False)
