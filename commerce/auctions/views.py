from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Listing, Bid, Comment, Watchlist

CATEGORIES = ["Books", "Electronics", "Fashion", "Food", "Furniture", "Gadgets", "Health", "Home", "Property", "Sports", "Toys"]

class ListingForm(forms.Form):
    CATEGORY_CHOICES = [("", "Select a category")] + [(category, category) for category in CATEGORIES]

    title = forms.CharField(max_length=200, required=True, label="", widget=forms.TextInput(attrs={"class": "form-control mb-3", "placeholder": "Enter your title"}))
    description = forms.CharField(max_length=200, required=True, label="", widget=forms.Textarea(attrs={"class": "form-control mb-3", "placeholder": "A short description", "rows" : "3"}))
    starting_bid = forms.FloatField(min_value=0, required=True, label="", widget=forms.NumberInput(attrs={"class": "form-control mb-3", "placeholder": "Starting bid"}))
    image_url = forms.CharField(max_length=200, required=False, label="", widget=forms.TextInput(attrs={"class": "form-control mb-3", "placeholder": "Enter image url (Optional)"}))
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=False, label="", widget=forms.Select(attrs={"class": "form-control mb-3"}))


def index(request):
    category_name = request.GET.get('category')
    if category_name:
        listings = Listing.objects.filter(category=category_name, is_active=True)
    else:
        listings = Listing.objects.filter(is_active=True)

    return render(request, "auctions/index.html", {
        "listings": listings,
        "category_name": category_name,
    })


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": CATEGORIES,
    })


@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            image_url = form.cleaned_data["image_url"]
            category = form.cleaned_data["category"]
            user = request.user

            listing = Listing(
                title=title,
                description=description,
                starting_bid=starting_bid,
                current_price=starting_bid,
                image_url=image_url,
                category=category,
                user=user,
            )

            listing.save()

            return HttpResponseRedirect(reverse("index"))

        else:
            return render(request, "auctions/create.html", {
                "categories": CATEGORIES,
                "form": form,
            })

    return render(request, "auctions/create.html", {
        "categories": CATEGORIES,
        "form": ListingForm,
    })


@login_required
def close_listing(request, id):
    listing = Listing.objects.get(pk=id, user=request.user)
    listing.is_active = False
    listing.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def listings(request, id):
    listing = Listing.objects.get(pk=id)
    watchlisted = Watchlist.objects.filter(user=request.user, listing=listing)
    bids = Bid.objects.filter(listing=listing)
    comments = Comment.objects.filter(listing=listing)

    return render(request, "auctions/listings.html", {
        "listing": listing,
        "watchlisted": watchlisted,
        "bids_count": bids.count,
        "last_bider": bids.last().user if bids.exists() else None,
        "comments": comments,
    })


@login_required
def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "watchlists": Watchlist.objects.filter(user=request.user),
    })


@login_required
def to_watchlist(request, id):
    # Check if id already exists
    user = request.user
    listing = Listing.objects.get(pk=id)
    watchlist = Watchlist.objects.filter(user=user, listing=listing)

    if watchlist.exists():
        watchlist.delete()
    else:
        watchlist = Watchlist(user=user, listing=listing)
        watchlist.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def place_bid(request, id):
    if request.method == "POST":
        user = request.user
        listing = Listing.objects.get(pk=id, is_active=True)
        bid_amount = float(request.POST["bid"])

        # Check if no bids have been placed yet
        if not Bid.objects.filter(listing=listing).exists():
            if bid_amount >= listing.starting_bid:
                bid = Bid(user=user, listing=listing, amount=bid_amount)
                bid.save()
                listing.current_price = bid_amount
                listing.save()
            else:
                messages.error(request, "Bid amount must be at least the starting bid!")
               
        elif bid_amount > listing.current_price:
            bid = Bid(user=user, listing=listing, amount=bid_amount)
            bid.save()
            listing.current_price = bid_amount
            listing.save()
        else:
            messages.error(request, "Bid amount must be greater than the current price!")

        # Redirect back to the same page
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # If the method is not POST, redirect to the listing page
    return redirect("listing", id=id)


@login_required
def add_comment(request):
    if request.method == "POST":
        user = request.user
        listing = Listing.objects.get(pk=request.POST["listing"])
        comment = request.POST["comment"]

        comment = Comment(user=user, listing=listing, comment=comment)
        comment.save()

        return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def delete_comment(request):
    if request.method == "POST":
        user = request.user
        comment = Comment.objects.get(pk=request.POST["comment_id"], user=user)
        comment.delete()

        return redirect(request.META.get('HTTP_REFERER', '/'))


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
