from django.db import models

class Author(models.Model):
    scholar_id = models.IntegerField(null=True, unique=True)
    email = models.CharField(blank=False, null=False, max_length=255, unique=True)
    first_name = models.CharField(blank=False, null=False, max_length=255)
    last_name = models.CharField(blank=False, null=False, max_length=255)
    submitter = models.BooleanField(default=False)
    first_author = models.BooleanField(default=False)
    volunteer = models.BooleanField(default=False)
    bids = models.ManyToManyField('Paper', through='Bid', related_name='bids')
    papers = models.ManyToManyField('Paper', through='Authorship', related_name='authors')

    def __str__(self):
        return self.email

class Paper(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(blank=False, null=False, max_length=255)
    abstract = models.TextField(blank=False, null=False)

    def __str__(self):
        return "<{id}: {title!r}>".format(**self.__dict__)

class Bid(models.Model):
    author = models.ForeignKey(Author, null=False, on_delete="cascade")
    paper = models.ForeignKey(Paper, null=False, on_delete="cascade")
    score = models.IntegerField(null=False)
    weight = models.FloatField(null=True)

    class Meta:
        unique_together = ('author', 'paper')

class Authorship(models.Model):
    author = models.ForeignKey(Author, null=False, on_delete="cascade")
    paper = models.ForeignKey(Paper, null=False, on_delete="cascade")
    number = models.IntegerField(null=False)

from django.contrib import admin
admin.site.register(Author)
admin.site.register(Paper)
