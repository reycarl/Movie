from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Genre(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)
    year = models.PositiveIntegerField()
    runtime_minutes = models.PositiveIntegerField(default=120)
    synopsis = models.TextField()
    poster = models.ImageField(upload_to="posters/", blank=True, null=True)
    trailer_url = models.URLField(blank=True)
    genres = models.ManyToManyField(Genre, blank=True, related_name="movies")
    is_published = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.year}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("movie_detail", args=[self.slug])

    @property
    def average_rating(self):
        value = self.reviews.aggregate(avg=models.Avg("rating"))["avg"]
        return round(value, 1) if value is not None else 0

    def __str__(self):
        return f"{self.title} ({self.year})"


class CastMember(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="cast")
    name = models.CharField(max_length=120)
    character = models.CharField(max_length=120, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name} – {self.movie.title}"


class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    author_name = models.CharField(max_length=80)
    rating = models.PositiveIntegerField()
    body = models.TextField(max_length=500)
    has_spoilers = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_created"]

    def clean(self):
        from django.core.exceptions import ValidationError
        if not 1 <= self.rating <= 10:
            raise ValidationError({"rating": "Rating must be from 1 to 10."})
        if len(self.body.strip()) < 20:
            raise ValidationError({"body": "Review must be at least 20 characters."})

    def __str__(self):
        return f"{self.author_name} – {self.movie.title}"


class WatchlistItem(models.Model):
    STATUS_CHOICES = [
        ("want", "Want to Watch"),
        ("watched", "Watched"),
    ]
    session_key = models.CharField(max_length=40)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="watchlist_items")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="want")
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session_key", "movie"],
                name="unique_session_movie"
            )
        ]
        ordering = ["-date_added"]

    def __str__(self):
        return f"{self.session_key} – {self.movie.title}"
