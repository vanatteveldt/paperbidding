import hashlib

from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

# Create your views here.
from bidding.models import Paper, Author, Bid


def get_hash(email):
    h = hashlib.sha1()
    h.update(settings.SECRET_KEY.encode("utf-8"))
    h.update(email.encode("utf-8"))
    return h.hexdigest()


def index(request):
    if not ('email' in request.GET and 'code' in request.GET):
        return HttpResponse('HTTP 401 Unauthorized: please provide email and code in GET parameters', status=401)
    email = request.GET['email']
    code = request.GET['code']
    if code != get_hash(email):
        return HttpResponse('HTTP 401 Unauthorized: code does not match email', status=401)

    me = Author.objects.get(email=request.GET['email'])
    papers = Paper.objects.all()

    papers = [p for p in papers if email not in p.author_emails]
    bids = {bid.paper_id: bid for bid in me.bid_set.all()}

    if request.POST:
        for paper, score in request.POST.items():
            if not paper.startswith("paper_"): continue
            pid = int(paper.split("_")[1])
            score = int(score)
            if pid in bids:
                if bids[pid].score != score:
                    bids[pid].score = score
                    bids[pid].save()
            elif score != 0:
                bids[pid] = Bid.objects.create(paper_id=pid, author=me, score=score)
    nbids = len([b for pid, b in bids.items() if b.score > 0])
    has_bids = any(b.score != 0 for pid, b in bids.items())
    print(has_bids)

    if request.POST:
        msg = "Thanks for indicating your reviewing preferences!"
        nbids = len([b for pid,b in bids.items() if b.score > 0])
        if nbids < 10:
            warn = " Please bid 'yes' on at least 10 papers to ensure we can assign you papers that you are interested in!"

    for paper in papers:
        if paper.id in bids:
            paper.score = bids[paper.id].score
            paper.weight = bids[paper.id].weight
        else:
            paper.score = 0
            paper.weight=0

        if paper.weight is None:
            paper.weight = 0


    papers.sort(key=lambda p:-p.weight)

    for paper in papers:
        if 'topicminer' in paper.title.lower():
            print(paper.title, paper.score)


    return render(request, 'bidding/bids.html', locals())

