from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
from bidding.models import Paper, Author


def index(request):
    me = Author.objects.get(last_name='Welbers')
    papers = Paper.objects.all()
    return render(request, 'bidding/bids.html', locals())

