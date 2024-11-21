from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("close_listing/<int:id>", views.close_listing, name="close_listing"),
    path("listings/<int:id>", views.listings, name="listings"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("to_watchlist/<int:id>", views.to_watchlist, name="to_watchlist"),
    path("place_bid/<int:id>", views.place_bid, name="place_bid"),
    path("add_comment", views.add_comment, name="add_comment"),
    path("delete_comment", views.delete_comment, name="delete_comment"),
]
