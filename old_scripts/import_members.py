import csv, sys
import django; django.setup()
from bidding.models import Author, Paper

members = list(csv.DictReader(sys.stdin))

# Web_Site_Member_ID,Membership,First_Name,Last_Name,Email_Address,Home_Country

for v in members:
    email = v['Email_Address']
    if not Author.objects.filter(email=email).exists():
        print(email)
        Author.objects.create(id=v['Web_Site_Member_ID'], email=email,
                              first_name=v['First_Name'], last_name=v['Last_Name'],
                              affiliation="?", submitter=False, volunteer=False)
