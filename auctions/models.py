from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey

CATEGORIES = (
    ('Other', 'Other'),
    ('Fashion', 'Fashion'),
    ('Toys', 'Toys'),
    ('Electronics', 'Electronics'),
    ('Home', 'Home')
)

class User(AbstractUser):
    pass

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=512)

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Listings")
    title = models.CharField(max_length=256)
    description = models.CharField(max_length=512)
    image = models.URLField(null=True, blank=True)
    category = models.CharField(max_length=256, choices=CATEGORIES, default=CATEGORIES[1][1])
    price = models.PositiveIntegerField()
    current_bid = models.ForeignKey(Bid, null=True, blank=True, on_delete=models.CASCADE)
    watchers = models.ManyToManyField(User, blank=True, null=True, related_name="watching")
    comments = models.ManyToManyField(Comment, blank=True)
    active = models.BooleanField(default=True)