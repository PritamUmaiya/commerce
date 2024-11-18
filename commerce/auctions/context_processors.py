from .models import Watchlist

def watchlist_count(request):
    if request.user.is_authenticated:
        return {"watchlist_count": Watchlist.objects.filter(user=request.user).count()}
    return {"watchlist_count": 0}