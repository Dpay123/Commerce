from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.forms import ModelForm, HiddenInput
from matplotlib import widgets
from pytz import common_timezones

from .models import *

class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['item', 'description', 'starting_bid', 'category', 'img_url', 'seller']
        widgets = {'seller': HiddenInput()}

class NewBidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['bid']

class NewCommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['comment']

class NewWatchForm(ModelForm):
    class Meta:
        model = Watchlist
        fields = ['user', 'listing']

def check_if_watched(user, listing):
    if not user.watchlist.filter(listing = listing):
        return False
    return True

def check_if_seller(user, listing):
    if user == listing.seller:
        return True
    return False

def check_if_winner(user, listing):
    try:
        if not check_if_seller(user, listing):
            highest_bid = Bid.objects.get(bidding_on=listing, bid=listing.current_bid)
            return highest_bid.bidder == user
        else:
            return False
    except ObjectDoesNotExist:
        return False

def is_valid(bid, listing):
    if bid > listing.starting_bid and (listing.current_bid is None or bid > listing.current_bid):
        return True
    else:
        return False

def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    comments = Comment.objects.filter(auction=listing)
    if listing.current_bid == None:
        listing.current_bid = listing.starting_bid
    # if logged in
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)
        watched = check_if_watched(user, listing)
        seller = check_if_seller(user, listing)
        winner = check_if_winner(user, listing)
    else:
        watched = False
        seller = False
        winner = False

    context = {
        "listing": listing,
        "comments": comments,
        "bid_form": NewBidForm(),
        "watch_form": NewWatchForm(),
        "comment_form": NewCommentForm(),
        "watched": watched,
        "seller": seller,
        "closed": listing.closed,
        "winner": winner
    }

    if request.method == "POST" and request.user.is_authenticated:
        if request.POST.get("button") == "Close":
            listing.closed = True
            listing.save()
            return HttpResponseRedirect(reverse('listing', args=(listing.id,)))
        elif request.POST.get("button") == "Watchlist":
            if not watched:
                watchlist = Watchlist()
                watchlist.user = user
                watchlist.listing = listing
                watchlist.save()
            else:
                user.watchlist.filter(listing=listing).delete()
            return HttpResponseRedirect(reverse('listing', args=(listing.id,)))
        elif request.POST.get("button") == "comment":
            form = NewCommentForm(request.POST)
            if form.is_valid():
                new_comment = form.save(commit=False)
                new_comment.author = user
                new_comment.auction = listing
                new_comment.save()
                return render(request, "auctions/listing.html", context)
        else:
            bid = float(request.POST['bid'])
            if is_valid(bid, listing):
                form = NewBidForm(request.POST)
                newBid = form.save(commit=False)
                newBid.bidding_on = listing
                newBid.bid = bid
                newBid.bidder = user
                newBid.save()
                listing.current_bid = bid
                listing.save()
                return render(request, "auctions/listing.html", context)
            else:
                context["bid_error"] = "Bid must exceed current"
                return render(request, "auctions/listing.html", context)

    # if POST but not logged in
    elif request.method == 'POST' and not request.user.is_authenticated:
        context["error"] = "You must be logged in"
        return render(request, "auctions/listing.html", context)

    # if GET request
    else:
        return render(request, "auctions/listing.html", context)

 
def categories(request):
    category_list = []
    for i in CATEGORY:
        category_list.append(i[0])
    context = {
        "categories": category_list
    }
    return render(request, "auctions/categories.html", context)

def search_category(request, category):
    listings = Listing.objects.filter(category = category)
    context = {
        "listings": listings
    }
    return render(request, "auctions/index.html", context)

@login_required
def watchlist(request):
    user = request.user
    watched_items = user.watchlist.filter(user_id = user)
    for listing in watched_items:
        if listing.listing.current_bid == None:
            listing.listing.current_bid = listing.listing.starting_bid
    context = {
        "watchlist": watched_items
    }
    return render(request, "auctions/watchlist.html", context)

def index(request):
    listings = Listing.objects.filter()
    for listing in listings:
        if listing.current_bid == None:
            listing.current_bid = listing.starting_bid
    context = {
        "listings": listings
    }
    return render(request, "auctions/index.html", context)

@login_required
def create(request):
    if request.method == "GET":
        form = NewListingForm()
        context = {
            "form": form
        }
        return render(request, "auctions/create.html", context)

    else:
        form = NewListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            if not listing.img_url:
                listing.img_url = "https://www.daveraine.com/img/products/no-image.jpg"
            listing.save()
            return redirect("index")
        else:
            return HttpResponse("Invalid Form")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
