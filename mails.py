import csv, sys
import django;

django.setup()
from bidding.views import get_hash

from bidding.models import Author, Paper

for author in Author.objects.all():
    print(author.email, get_hash(author.email))