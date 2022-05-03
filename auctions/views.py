from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.forms import ModelForm, HiddenInput

from .models import *

class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['item', 'description', 'starting_bid', 'category', 'img_url', 'seller']
        widgets = {'seller': HiddenInput()}

def item(request, item):
    item_lookup = Listing.objects.get(item = item)
    comments = Comment.objects.all()
    context = {
        "item": item_lookup,
        "comments": comments
    }
    return render(request, "auctions/item.html", context)

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

def watched(request):
    user = request.user
    watched_items = Watchlist.objects.filter(user = user)
    context = {
        "watchlist": watched_items
    }
    return render(request, "auctions/watchlist.html", context)

def index(request):
    listings = Listing.objects.all()
    context = {
        "listings": listings
    }
    return render(request, "auctions/index.html", context)

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
