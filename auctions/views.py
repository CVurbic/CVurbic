from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from .models import User, AuctionListing, Watchlist, Bid, Comment

from .forms import CreateListingForm, BidForm

def index(request):
    return render(request, "auctions/active_listings.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("active_listings"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("active_listings"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("active_listings"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if request.method == 'POST':
        form = CreateListingForm(request.POST, user=request.user)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.current_bid = listing.starting_bid
            listing.save()
            return redirect('active_listings')
    else:
        form = CreateListingForm(user=request.user)

    return render(request, 'auctions/create_listing.html', {'form': form})



def active_listings(request):
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')

    active_listings = AuctionListing.objects.all()

    if status_filter:
        active_listings = active_listings.filter(status=status_filter)

    categories = AuctionListing.objects.values_list('category', flat=True).distinct()

    if category_filter:
        active_listings = active_listings.filter(category=category_filter)

    return render(request, 'auctions/active_listings.html', {'active_listings': active_listings, 'categories': categories})



def listing_details(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    bids = Bid.objects.filter(auction_listing=listing).order_by('-bid_amount')

    is_creator = request.user == listing.creator

    winner = None
    if listing.status == 'closed' and bids:
        winner = bids.order_by('-bid_amount').first().bidder

    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            bid_amount = form.cleaned_data['bid_amount']

            if bid_amount >= listing.starting_bid and (not bids or bid_amount > bids[0].bid_amount):
              
                bid = form.save(commit=False)
                bid.bidder = request.user
                bid.auction_listing = listing
                bid.save()

                listing.current_bid = bid_amount
                listing.save()

                messages.success(request, 'Bid placed successfully!')
                return redirect('listing_details', listing_id=listing_id)
            else:
                messages.error(request, 'Invalid bid amount. Make sure it meets the criteria.')
    else:
        form = BidForm()

    comments = Comment.objects.filter(auction_listing=listing).order_by('-created_at')

    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')
        if comment_text:
            Comment.objects.create(user=request.user, auction_listing=listing, text=comment_text)

    return render(
        request,
        'auctions/listing_details.html',
        {'listing': listing, 'bids': bids, 'form': form, 'is_creator': is_creator, 'winner': winner, 'comments': comments}
    )


def add_to_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    watchlist, created = Watchlist.objects.get_or_create(user=request.user)

    if listing in watchlist.listings.all():
        watchlist.listings.remove(listing)
    else:
        watchlist.listings.add(listing)

    return HttpResponseRedirect(reverse('listing_details', args=[listing_id]))


def bid(request, listing_id):
    if request.method == 'POST':
        bid_amount = request.POST.get('bid_amount')
        listing = get_object_or_404(AuctionListing, pk=listing_id)

        if not bid_amount or float(bid_amount) < float(listing.starting_bid):
            messages.warning(request, 'Bid must be at least as large as the starting bid.')
        elif float(bid_amount) <= float(listing.current_bid):
            messages.warning(request, 'Bid must be greater than the current highest bid.')

        else:
            Bid.objects.create(
                bidder=request.user,
                auction_listing=listing,
                bid_amount=bid_amount
            )
            listing.current_bid = bid_amount
            listing.save()
            messages.success(request, 'Bid placed successfully!')

    return redirect('listing_details', listing_id=listing_id)


def close_auction(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)

    if listing.status == 'closed':
        messages.error(request, 'This auction is already closed.')
        return redirect('listing_details', listing_id=listing_id)

    if request.user != listing.creator:
        messages.error(request, 'You are not authorized to close this auction.')
        return redirect('listing_details', listing_id=listing_id)

    bids = Bid.objects.filter(auction_listing=listing)

    if bids:
        winning_bid = bids.order_by('-bid_amount').first()

        listing.winning_bid = winning_bid
        listing.status = 'closed'
        listing.save()

        messages.success(request, f'The auction for "{listing.title}"  has been closed. The winner is: {winning_bid.bidder.username}.')
    else:
        listing.status = 'inactive'
        listing.save()

        messages.info(request, 'The auction has been closed with no bids.')

    return redirect('listing_details', listing_id=listing_id)


@login_required
def watchlist(request):
    user_watchlist = Watchlist.objects.get_or_create(user=request.user)[0]
    watchlist_listings = user_watchlist.listings.all()
    return render(request, 'auctions/watchlist.html', {'watchlist_listings': watchlist_listings})

def remove_from_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    watchlist = Watchlist.objects.get(user=request.user)

    if listing in watchlist.listings.all():
        watchlist.listings.remove(listing)

    return redirect('watchlist')



def category_listings(request, category):
    active_category_listings = AuctionListing.objects.filter(category=category, status='open')

    return render(request, 'auctions/category_listings.html', {'category': category, 'listings': active_category_listings})