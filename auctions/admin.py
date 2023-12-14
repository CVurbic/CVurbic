from django.contrib import admin
from .models import AuctionListing, Bid, Comment, Watchlist,Category

# Register your models here.

@admin.register(AuctionListing)
class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'starting_bid', 'current_bid', 'status', 'creator', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description', 'creator__username')

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('bidder', 'auction_listing', 'bid_amount', 'bid_time')
    list_filter = ('auction_listing__title', 'bidder__username')
    search_fields = ('auction_listing__title', 'bidder__username')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'auction_listing', 'text', 'created_at')
    list_filter = ('auction_listing__title', 'user__username')
    search_fields = ('auction_listing__title', 'user__username')

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', )
    search_fields = ('user__username',)



admin.site.register(Category)