from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User

CATEGORIES = ["Books", "Electronics", "Fashion", "Food", "Furniture", "Gadgets", "Health", "Home", "Property", "Sports", "Toys"]

class ListingForm(forms.Form):
    CATEGORY_CHOICES = [(category, category) for category in CATEGORIES]

    title = forms.CharField(max_length=200, required=True, label="", widget=forms.TextInput(attrs={"class": "form-control mb-3", "placeholder": "Enter your title"}))
    description = forms.CharField(max_length=200, required=True, label="", widget=forms.Textarea(attrs={"class": "form-control mb-3", "placeholder": "A short description", "rows" : "3"}))
    starting_bid = forms.IntegerField(min_value=0, required=True, label="", widget=forms.NumberInput(attrs={"class": "form-control mb-3", "placeholder": "Starting bid"}))
    image_url = forms.CharField(max_length=200, required=True, label="", widget=forms.TextInput(attrs={"class": "form-control mb-3", "placeholder": "Enter image url (Optional)"}))
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=True, label="", widget=forms.Select(attrs={"class": "form-control mb-3"}))


def index(request):
    return render(request, "auctions/index.html")

def create_listing(request):
    return render(request, "auctions/create.html", {
        "categories": CATEGORIES,
        "form": ListingForm,
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
