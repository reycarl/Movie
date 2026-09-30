# CineBase – Alpine.js + Django + HTMX Performance Task

CineBase is a server-rendered movie database enhanced with Alpine.js for small,
instant client-side UI state and HTMX for server requests.

## Technology split

- **Django**: database models, validation, server-rendered HTML, movie/review/watchlist persistence.
- **HTMX**: search requests, review submission, watchlist add/remove requests, and partial HTML swaps.
- **Alpine.js**: menus, theme state, tabs, modals, star preview, counters, filters, sorting, wizard state, cast rows, and other UI-only behavior.
- **SQLite**: included as the default development database.
- **No React/Vue/jQuery/build step**.

## Alpine.js hosting reason

This project uses a pinned Alpine.js CDN version with `defer` because the performance task permits
a pinned CDN version, keeps the project free from a frontend build step, and makes the dependency
easy to inspect. Alpine's Persist plugin is also loaded from the same pinned CDN.

> **Script order:** in `base.html` the Persist plugin and `static/js/alpine.js` load *before* Alpine core,
> because Alpine's CDN build starts immediately and our `alpine:init` listener must already exist.

## Requirements

- Python 3.10+
- Django 5.2+
- Pillow

## Setup

### Windows PowerShell

```powershell
cd CineBase_AlpineJS
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py manage.py migrate
py manage.py loaddata cinebase/fixtures/sample_movies.json
py manage.py runserver
```

Open http://127.0.0.1:8000/

### macOS/Linux

```bash
cd CineBase_AlpineJS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata cinebase/fixtures/sample_movies.json
python manage.py runserver
```

## Main pages

- `/` – Movie Catalog and HTMX search
- `/movies/<slug>/` – Movie Detail
- `/watchlist/` – My Watchlist
- `/manage/movies/new/` – Editor Movie Management
- `/admin/` – Django admin after creating a superuser

## Create an editor/admin account

```bash
python manage.py createsuperuser
```

The performance task does not require user accounts for watchlists, so the normal watchlist uses
the Django session. The admin account is only for Django administration.

## Alpine components included

| Component | Page |
|---|---|
| navbarMenu | Global/base |
| theme | Global/base store |
| toast stack | Global/base |
| watchlist store | Global/base |
| genreFilter | Catalog |
| filterDrawer | Catalog |
| movieCard | Catalog |
| viewMode | Catalog |
| tabs | Detail |
| trailerModal | Detail |
| starRating | Detail |
| reviewComposer | Detail |
| spoilerList | Detail |
| watchlistPage | Watchlist |
| confirmRemove | Watchlist |
| movieWizard | Management |
| castRows | Management |
| genrePicker | Management |

## Alpine requirements demonstrated

- `x-data`
- `x-init`
- `x-show`
- `x-if`
- `x-for` with `:key`
- `x-model`, `.number`, `.trim`, `.debounce`
- `x-bind` / `:class`, `:disabled`, `:style`, `:aria-*`
- `x-on` / `@click`, `.prevent`, `.stop`, `.window`, `.outside`, `.debounce`, `.once`
- `x-text`
- `x-transition`
- `x-ref`
- `x-effect`
- `x-cloak`
- `x-teleport`
- `$el`
- `$refs`
- `$nextTick`
- `$watch`
- `$dispatch`
- two computed getters: `filteredItems`, `totalRuntime`, plus `canAdvance`
- Alpine stores for theme, toasts, and watchlist
- persisted theme/view state

## HTMX + Alpine integration points

1. Catalog filters and genre chips feed values into the HTMX request. The server still performs the
   actual database filtering and returns `_movie_grid.html`.
2. The catalog listens to `htmx:before-request` and `htmx:after-request` to show a client-side loading
   state while the server-rendered grid is replaced.
3. Watchlist buttons update Alpine optimistically, then use HTMX to persist the change on the server.
4. The review form is validated and saved by Django; the returned partial is swapped into the page.
5. Django can send an `HX-Trigger` response header containing a toast event. Alpine receives it with
   `@toast.window`.
6. The movie wizard lives outside its HTMX validation target, so its Alpine step state can remain
   active while Django returns validation HTML.
7. Server data for the watchlist is passed through `json_script` instead of being inserted into raw JS.

## Important design boundary

Do not put the authoritative movie list, review data, or saved watchlist into Alpine. Alpine only
keeps temporary UI state. Django owns persistent data and validation.

## Demo checklist

For a 4–5 minute recording:

1. Show the mobile navbar opening, closing, Escape behavior, and theme toggle.
2. Search for a movie and show HTMX loading + server-rendered results.
3. Select genre chips, adjust year/rating sliders, and switch grid/list mode.
4. Open a movie and demonstrate tabs, read-more, trailer modal, star hover/click, review counter,
   and spoiler reveal.
5. Add/remove a movie from the watchlist and show the navbar count.
6. In `/watchlist/`, demonstrate status tabs, sorting, bulk selection, combined runtime, and removal.
7. Open the editor wizard and demonstrate slug preview, genre tags, dynamic cast rows, poster preview,
   character/word counter, validation, and unsaved-change warning.
8. Resize to mobile and show responsive layout.

## Submission

The assignment asks for a Word document containing page snippets and a public GitHub repository link.
It also specifies the file format `LastName_LastName.docx` and a Google Drive submission folder.

Submit:
- this project folder or GitHub repository,
- `Part1_UI_State_Analysis.docx`,
- the Word document with page screenshots/snippets and GitHub link,
- 4–5 minute screen recording/live demo,
- short reflection.

See `SUBMISSION_GUIDE.md` for a step-by-step checklist.


## Included submission documents

- `Part1_UI_State_Analysis.docx` – Part 1 analysis starter document.
- `Final_Submission_Document.docx` – screenshot/snippet submission template.
- `REFLECTION.md` – short reflection draft.
- `SUBMISSION_GUIDE.md` – detailed setup, demo, and submission checklist.

The Word files are templates/starter materials. Add your own screenshots, name, section, GitHub URL,
and any instructor-specific information before submitting.
