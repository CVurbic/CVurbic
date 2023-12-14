from django.urls import path
from .views import create_listing, active_listings, listing_details, add_to_watchlist, bid, watchlist, remove_from_watchlist, category_listings

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create_listing', create_listing, name='create_listing'),
    path('active_listings', active_listings, name='active_listings'),
    path('listing/<int:listing_id>/', listing_details, name='listing_details'),
    path('listing/<int:listing_id>/add_to_watchlist/', add_to_watchlist, name='add_to_watchlist'),
    path('bid/<int:listing_id>/', bid, name='bid'),
    path('listing/<int:listing_id>/close/', views.close_auction, name='close_auction'),
    path('listing/<int:listing_id>/remove_from_watchlist/', remove_from_watchlist, name='remove_from_watchlist'),
    path('watchlist/', watchlist, name='watchlist'),
    path('category/<str:category>/', category_listings, name='category_listings'),
]
