from django.urls import path
from . import views

urlpatterns = [
    path("", views.movie_list, name="movie_list"),
    path("movies/<slug:slug>/", views.movie_detail, name="movie_detail"),
    path("movies/<slug:slug>/review/", views.submit_review, name="submit_review"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("watchlist/<int:movie_id>/toggle/", views.toggle_watchlist, name="toggle_watchlist"),
    path("watchlist/<int:item_id>/remove/", views.remove_watchlist, name="remove_watchlist"),
    path("watchlist/<int:item_id>/status/", views.update_watchlist_status, name="update_watchlist_status"),
    path("manage/movies/new/", views.movie_create, name="movie_create"),
]
