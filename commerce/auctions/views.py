from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Watchlist, Bid, Comment


class ListingForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={"class": "form-control mb-3"}))
    description = forms.CharField(label="Description", widget=forms.Textarea(attrs={"class": "form-control mb-3", "rows": "2"}))
    starting_bid = forms.DecimalField(label="Starting Bid", widget=forms.TextInput(attrs={"class": "form-control mb-3"}))
    image_url = forms.URLField(label="Image URL (Optional)", required=False, widget=forms.TextInput(attrs={"class": "form-control mb-3"}))
    category = forms.CharField(label="Category (Optional)", required=False, widget=forms.TextInput(attrs={"class": "form-control  mb-3"}))


def index(request):
    listings = Listing.objects.all()
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
        
        if not username or not email or not password or not confirmation:
            return render(request, "auctions/register.html", {
                "message": "All fields are required."
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


def create(request):
    """Create a new listing"""
    if request.method == "POST":
        form = ListingForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            image_url = form.cleaned_data["image_url"]
            category = form.cleaned_data["category"]

            # Create a new listing
            listing = Listing(
                title=title,
                description=description,
                starting_bid=starting_bid,
                current_bid=starting_bid,
                image_url=image_url,
                category=category,
                user=request.user
            )
            listing.save()
        
            return HttpResponseRedirect(reverse("index"))

        else:
            return render(request, "auctions/create.html", {
                "form": form
            })

    else:
        return render(request, "auctions/create.html", {
            "form": ListingForm()
        })
