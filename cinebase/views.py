import json
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from .forms import MovieForm, ReviewForm
from .models import CastMember, Genre, Movie, Review, WatchlistItem


def ensure_session(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def watchlist_count(request):
    key = ensure_session(request)
    return WatchlistItem.objects.filter(session_key=key).count()


def movie_list(request):
    movies = Movie.objects.filter(is_published=True).prefetch_related("genres", "cast")
    genres = Genre.objects.all()
    q = request.GET.get("q", "").strip()
    selected_genres = request.GET.getlist("genres")
    min_year = request.GET.get("min_year", "")
    max_year = request.GET.get("max_year", "")
    min_rating = request.GET.get("min_rating", "")

    if q:
        movies = movies.filter(Q(title__icontains=q) | Q(synopsis__icontains=q))
    if selected_genres:
        movies = movies.filter(genres__slug__in=selected_genres).distinct()
    if min_year:
        try:
            movies = movies.filter(year__gte=int(min_year))
        except ValueError:
            pass
    if max_year:
        try:
            movies = movies.filter(year__lte=int(max_year))
        except ValueError:
            pass
    if min_rating:
        try:
            movies = movies.filter(reviews__rating__gte=float(min_rating)).distinct()
        except ValueError:
            pass

    key = ensure_session(request)
    context = {
        "movies": movies,
        "genres": genres,
        "selected_genres": selected_genres,
        "watchlist_ids": list(
            WatchlistItem.objects.filter(session_key=key).values_list("movie_id", flat=True)
        ),
        "query": q,
        "min_year": min_year or 1990,
        "max_year": max_year or 2026,
        "min_rating": min_rating or 0,
        "watchlist_count": watchlist_count(request),
    }
    if request.headers.get("HX-Request"):
        return render(request, "partials/_movie_grid.html", context)
    return render(request, "movie_list.html", context)


def movie_detail(request, slug):
    movie = get_object_or_404(
        Movie.objects.prefetch_related("genres", "cast", "reviews"),
        slug=slug,
        is_published=True,
    )
    key = ensure_session(request)
    watch_item = WatchlistItem.objects.filter(session_key=key, movie=movie).first()
    review_form = ReviewForm()
    return render(
        request,
        "movie_detail.html",
        {
            "movie": movie,
            "review_form": review_form,
            "in_watchlist": bool(watch_item),
            "watchlist_count": watchlist_count(request),
        },
    )


@require_POST
def submit_review(request, slug):
    movie = get_object_or_404(Movie, slug=slug, is_published=True)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.movie = movie
        review.save()
        html = render_to_string("partials/_reviews.html", {"movie": movie}, request=request)
        response = HttpResponse(html)
        response["HX-Trigger"] = json.dumps({"toast": {"message": "Review saved.", "type": "success"}})
        return response
    html = render_to_string(
        "partials/_review_form.html",
        {"movie": movie, "review_form": form},
        request=request,
    )
    return HttpResponse(html, status=422)


@require_POST
def toggle_watchlist(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id, is_published=True)
    key = ensure_session(request)
    item = WatchlistItem.objects.filter(session_key=key, movie=movie).first()
    if item:
        item.delete()
        action = "removed"
    else:
        WatchlistItem.objects.create(session_key=key, movie=movie)
        action = "added"

    count = watchlist_count(request)
    response = JsonResponse({
        "ok": True,
        "action": action,
        "count": count,
        "movie_id": movie.id,
    })
    response["HX-Trigger"] = json.dumps({
        "watchlist-updated": {"count": count, "movie_id": movie.id, "action": action},
        "toast": {
            "message": f"{movie.title} {action} to watchlist.",
            "type": "success",
        },
    })
    return response


def watchlist(request):
    key = ensure_session(request)
    items = list(
        WatchlistItem.objects.filter(session_key=key)
        .select_related("movie")
        .prefetch_related("movie__genres")
    )
    data = [
        {
            "id": item.id,
            "movie_id": item.movie_id,
            "title": item.movie.title,
            "year": item.movie.year,
            "runtime": item.movie.runtime_minutes,
            "rating": item.movie.average_rating,
            "status": item.status,
            "status_label": item.get_status_display(),
            "url": item.movie.get_absolute_url(),
        }
        for item in items
    ]
    return render(
        request,
        "watchlist.html",
        {
            "items": items,
            "watchlist_json": data,
            "watchlist_count": len(items),
        },
    )


@require_POST
def remove_watchlist(request, item_id):
    key = ensure_session(request)
    item = get_object_or_404(WatchlistItem, pk=item_id, session_key=key)
    title = item.movie.title
    item.delete()
    response = HttpResponse("")
    response["HX-Trigger"] = json.dumps({
        "toast": {"message": f"{title} removed from watchlist.", "type": "info"},
        "watchlist-updated": {"count": watchlist_count(request)},
    })
    return response


@require_POST
def update_watchlist_status(request, item_id):
    key = ensure_session(request)
    item = get_object_or_404(WatchlistItem, pk=item_id, session_key=key)
    status = request.POST.get("status")
    if status not in {"want", "watched"}:
        return HttpResponse("Invalid status", status=400)
    item.status = status
    item.save(update_fields=["status"])
    response = HttpResponse("")
    response["HX-Trigger"] = json.dumps({
        "toast": {"message": f"{item.movie.title} marked as {item.get_status_display()}.", "type": "success"}
    })
    return response


def movie_create(request):
    if request.method == "GET":
        form = MovieForm()
        genres = list(Genre.objects.values("id", "name"))
        return render(request, "movie_form.html", {
            "form": form,
            "genres": genres,
            "watchlist_count": watchlist_count(request),
        })

    form = MovieForm(request.POST, request.FILES)
    if form.is_valid():
        movie = form.save()
        cast_payload = request.POST.get("cast_json", "[]")
        try:
            cast_rows = json.loads(cast_payload)
        except json.JSONDecodeError:
            cast_rows = []
        for index, row in enumerate(cast_rows):
            name = str(row.get("name", "")).strip()
            character = str(row.get("character", "")).strip()
            if name:
                CastMember.objects.create(
                    movie=movie,
                    name=name,
                    character=character,
                    order=index,
                )
        response = HttpResponse()
        response["HX-Redirect"] = movie.get_absolute_url()
        return response

    return render(
        request,
        "partials/_movie_form_step.html",
        {"form": form},
        status=422,
    )
