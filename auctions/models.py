from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.conf import settings


class User(AbstractUser):
    watchlist = models.OneToOneField('Watchlist', related_name='user_watchlist', on_delete=models.CASCADE, null=True, blank=True)


class AuctionListing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    winning_bid = models.OneToOneField('Bid', null=True, blank=True, on_delete=models.SET_NULL)
   
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_listings', default=1) # Add other fields as needed

    def __str__(self):
        return self.title

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder.username} bid ${self.bid_amount} on {self.auction_listing.title}"
    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Watchlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='user_watchlist', on_delete=models.CASCADE)
    listings = models.ManyToManyField('AuctionListing', blank=True)

    def __str__(self):
        return f"{self.user.username}'s Watchlist"
    

    
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name