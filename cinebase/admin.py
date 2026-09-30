from django.contrib import admin
from .models import Genre, Movie, CastMember, Review, WatchlistItem

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "runtime_minutes", "is_published")
    list_filter = ("is_published", "year", "genres")
    search_fields = ("title", "synopsis")
    prepopulated_fields = {"slug": ("title",)}

@admin.register(CastMember)
class CastMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "character", "movie", "order")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("author_name", "movie", "rating", "has_spoilers", "date_created")
    list_filter = ("rating", "has_spoilers")

@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ("session_key", "movie", "status", "date_added")
    list_filter = ("status",)
