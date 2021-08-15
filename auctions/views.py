from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Comment, CATEGORIES

class NewListingForm(forms.Form):
    title = forms.CharField(label="Title", max_length=256, required=True)
    description = forms.CharField(label="Description", max_length=512)
    price = forms.IntegerField(label="Price", min_value=0)
    image = forms.URLField(required=False)
    category = forms.ChoiceField(choices=CATEGORIES)

def index(request):
    listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })

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

@csrf_exempt
@login_required
def create(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            listing = Listing.objects.create(
                user = request.user,
                title = form.cleaned_data["title"],
                description = form.cleaned_data["description"],
                price = form.cleaned_data["price"],
                image = form.cleaned_data["image"],
                category = form.cleaned_data["category"]
            )
        else:
            return render(request, "auctions/create.html", {
                "form": form
            })
    return render(request, "auctions/create.html", {
        "form": NewListingForm()
    })

def listing(request, id):
    listing = Listing.objects.get(pk=id)
    return render(request, "auctions/listing.html", {
        "listing": listing
    })

@csrf_exempt
@login_required
def watch(request, id):
    listing = Listing.objects.get(pk=id)
    if request.method == "POST":
        if request.user in listing.watchers.all():
            listing.watchers.remove(request.user)
        else:
            listing.watchers.add(request.user)
    
    return render(request, "auctions/listing.html", {
        "listing": listing
    })

@csrf_exempt
@login_required
def bid(request, id):
    listing = Listing.objects.get(pk=id)
    if request.method == "POST" and listing.active:
        bid = int(request.POST.get("bid"))
        if bid is not None:
            if bid >= listing.price:
                listing.current_bid = Bid.objects.create(user=request.user, amount=bid)
                listing.price = listing.current_bid.amount + 1
                listing.save()
    
    return render(request, "auctions/listing.html", {
        "listing": listing
    })

@csrf_exempt
@login_required
def close(request, id):
    listing = Listing.objects.get(pk=id)
    if request.method == "POST":
        if request.user == listing.user:
            print("CLOSE")
            listing.active = False
            listing.save()
    
    return HttpResponseRedirect(reverse("listing", kwargs={'id':id}))

@csrf_exempt
@login_required
def comment(request, id):
    listing = Listing.objects.get(pk=id)
    if request.method == "POST" and listing.active:
        comment = Comment.objects.create(
            user=request.user,
            content=request.POST.get('content')
        )
        listing.comments.add(comment)
        listing.save()

    return HttpResponseRedirect(reverse("listing", kwargs={'id':id}))

def watchlist(request):
    listings = request.user.watching.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": CATEGORIES
    })

def category(request, category):
    print("CATEGORY")
    listings = Listing.objects.filter(category=category).all()
    return render(request, "auctions/category.html", {
        "category": category,
        "listings": listings
    })