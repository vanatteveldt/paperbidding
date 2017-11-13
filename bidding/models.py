from django.db import models

class Author(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(blank=False, null=False, max_length=255)
    email = models.CharField(blank=False, null=False, max_length=255, unique=True)
    first_name = models.CharField(blank=False, null=False, max_length=255)
    middle_name = models.CharField(blank=False, null=True, max_length=255)
    last_name = models.CharField(blank=False, null=False, max_length=255)
    affiliation = models.CharField(blank=False, null=False, max_length=255)
    submitter = models.BooleanField(default=True)
    volunteer = models.BooleanField(default=True)
    bids = models.ManyToManyField('Paper', through='Bid')

    def __str__(self):
        return self.email

class Paper(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.CharField(blank=False, null=False, max_length=255)
    title = models.CharField(blank=False, null=False, max_length=255)
    abstract = models.TextField(blank=False, null=False)
    first_author = models.ForeignKey(Author, null=False)
    author_emails = models.TextField()

    def __str__(self):
        return "<{id}: {title!r}>".format(**self.__dict__)

class Bid(models.Model):
    author = models.ForeignKey(Author, null=False)
    paper = models.ForeignKey(Paper, null=False)
    score = models.IntegerField(null=False)
    weight = models.FloatField(null=True)
    class Meta:
        unique_together = ('author', 'paper')

from django.contrib import admin
admin.site.register(Author)
admin.site.register(Paper)
