document.addEventListener("alpine:init", () => {
  Alpine.store("theme", {
    dark: false,
    init() {
      const saved = localStorage.getItem("cinebase-theme");
      this.dark = saved ? saved === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
      this.apply();
    },
    toggle() {
      this.dark = !this.dark;
      localStorage.setItem("cinebase-theme", this.dark ? "dark" : "light");
      this.apply();
    },
    apply() {
      document.documentElement.classList.toggle("dark", this.dark);
    }
  });

  Alpine.store("toasts", {
    items: [],
    add(message, type = "info") {
      const id = Date.now() + Math.random();
      this.items.push({ id, message, type });
      setTimeout(() => this.remove(id), 4000);
    },
    remove(id) {
      this.items = this.items.filter(item => item.id !== id);
    }
  });

  Alpine.store("watchlist", {
    count: 0,
    init() {
      const el = document.getElementById("watchlist-count-data");
      if (el) this.count = Number(el.textContent || 0);
    },
    setCount(value) {
      this.count = Number(value || 0);
    },
    adjust(delta) {
      this.count = Math.max(0, this.count + delta);
    }
  });

  Alpine.data("navbarMenu", () => ({
    open: false,
    init() {
      this.$watch("open", value => {
        if (value) this.$nextTick(() => this.$refs.closeButton?.focus());
      });
    },
    close() { this.open = false; }
  }));

  Alpine.data("genreFilter", (initial = []) => ({
    selected: initial,
    toggle(slug) {
      if (this.selected.includes(slug)) {
        this.selected = this.selected.filter(item => item !== slug);
      } else {
        this.selected.push(slug);
      }
      this.$dispatch("filter-changed", { genres: this.selected });
    },
    clear() {
      this.selected = [];
      this.$dispatch("filter-changed", { genres: [] });
    },
    get selectedCount() {
      return this.selected.length;
    }
  }));

  Alpine.data("filterDrawer", () => ({
    open: false,
    close() { this.open = false; }
  }));

  Alpine.data("movieCard", (movieId, inWatchlist = false) => ({
    quick: false,
    favorite: inWatchlist,
    init() {
      this.$el.dataset.movieId = movieId;
    },
    toggleFavorite() {
      const wasFavorite = this.favorite;
      this.favorite = !wasFavorite;
      Alpine.store("watchlist").adjust(this.favorite ? 1 : -1);
      this.$nextTick(() => {
        this.$refs.watchButton?.focus();
      });
    }
  }));

  Alpine.data("viewMode", () => ({
    mode: localStorage.getItem("cinebase-view") || "grid",
    setMode(mode) {
      this.mode = mode;
      localStorage.setItem("cinebase-view", mode);
    }
  }));

  Alpine.data("tabs", (initial = "overview") => ({
    active: initial,
    tabs: ["overview", "cast", "reviews"],
    select(tab) { this.active = tab; },
    move(direction) {
      const current = this.tabs.indexOf(this.active);
      const next = (current + direction + this.tabs.length) % this.tabs.length;
      this.active = this.tabs[next];
    }
  }));

  Alpine.data("trailerModal", (url = "") => ({
    open: false,
    url,
    init() {
      this.$watch("open", value => {
        document.body.style.overflow = value ? "hidden" : "";
      });
    },
    close() { this.open = false; }
  }));

  Alpine.data("starRating", (initial = 0) => ({
    value: Number(initial),
    hover: 0,
    labels: {
      0: "Choose a rating",
      1: "1 / 10 – Not for me",
      2: "2 / 10 – Weak",
      3: "3 / 10 – Below average",
      4: "4 / 10 – Okay",
      5: "5 / 10 – Average",
      6: "6 / 10 – Good",
      7: "7 / 10 – Very good",
      8: "8 / 10 – Great",
      9: "9 / 10 – Excellent",
      10: "10 / 10 – Outstanding"
    },
    get display() {
      return this.labels[this.hover || this.value] || this.labels[0];
    }
  }));

  Alpine.data("reviewComposer", () => ({
    body: "",
    min: 20,
    max: 500,
    get remaining() { return this.max - this.body.length; },
    get canSubmit() { return this.body.trim().length >= this.min && this.body.length <= this.max; },
    get progress() { return Math.min(100, (this.body.length / this.max) * 100); }
  }));

  Alpine.data("spoilerList", () => ({
    showAll: false
  }));

  Alpine.data("watchlistPage", (items = []) => ({
    items,
    status: "all",
    sortBy: "title",
    selected: [],
    get filteredItems() {
      const visible = this.status === "all" ? this.items : this.items.filter(item => item.status === this.status);
      return [...visible].sort((a, b) => {
        if (this.sortBy === "year") return b.year - a.year;
        if (this.sortBy === "rating") return b.rating - a.rating;
        return a.title.localeCompare(b.title);
      });
    },
    get totalRuntime() {
      return this.items.filter(item => this.selected.includes(item.id))
        .reduce((sum, item) => sum + Number(item.runtime || 0), 0);
    },
    toggleAll() {
      const ids = this.filteredItems.map(item => item.id);
      this.selected = this.selected.length === ids.length ? [] : ids;
    },
    removeLocal(id) {
      this.items = this.items.filter(item => item.id !== id);
      this.selected = this.selected.filter(item => item !== id);
    }
  }));

  Alpine.data("confirmRemove", (id) => ({
    open: false,
    id,
    confirm() {
      this.open = false;
      this.$refs.removeButton?.click();
    }
  }));

  Alpine.data("movieWizard", () => ({
    step: 1,
    dirty: false,
    title: "",
    year: 2026,
    runtime: 120,
    synopsis: "",
    genres: [],
    cast: [],
    posterName: "",
    posterUrl: "",
    genreSearch: "",
    availableGenres: [],
    init() {
      const genreData = document.getElementById("genre-data");
      if (genreData) this.availableGenres = JSON.parse(genreData.textContent);
      this.$watch("title", value => {
        this.dirty = true;
        this.$dispatch("slug-preview", { slug: this.slugPreview });
      });
      this.$watch("synopsis", () => this.dirty = true);
      window.addEventListener("beforeunload", this.beforeUnload);
    },
    destroy() {
      window.removeEventListener("beforeunload", this.beforeUnload);
    },
    get slugPreview() {
      return this.title.toLowerCase().trim()
        .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "movie-slug";
    },
    get wordCount() {
      return this.synopsis.trim() ? this.synopsis.trim().split(/\s+/).length : 0;
    },
    // A step can only advance while its required fields are filled in.
    get missingFields() {
      if (this.step !== 1) return [];
      const missing = [];
      if (!this.title.trim()) missing.push("title");
      if (!this.year || this.year < 1900 || this.year > 2100) missing.push("a valid year");
      if (!this.runtime || this.runtime < 1) missing.push("runtime");
      if (!this.synopsis.trim()) missing.push("synopsis");
      return missing;
    },
    get canAdvance() {
      return this.missingFields.length === 0;
    },
    get progress() {
      return Math.round((this.step / 3) * 100);
    },
    get synopsisHint() {
      const w = this.wordCount;
      if (w === 0) return "Recommended: 20–150 words";
      if (w < 20) return `Recommended: 20–150 words (${20 - w} more to go)`;
      if (w > 150) return "A bit long – recommended 20–150 words";
      return "Good length";
    },
    get wordLabel() {
      return `${this.wordCount} ${this.wordCount === 1 ? "word" : "words"}`;
    },
    get filteredGenres() {
      const q = this.genreSearch.toLowerCase().trim();
      return this.availableGenres.filter(g => g.name.toLowerCase().includes(q));
    },
    addCast() {
      this.cast.push({ name: "", character: "" });
      this.dirty = true;
      this.$nextTick(() => {
        const inputs = this.$el.querySelectorAll(".cast-row input:first-child");
        inputs[inputs.length - 1]?.focus();
      });
    },
    removeCast(index) {
      this.cast.splice(index, 1);
      this.dirty = true;
    },
    toggleGenre(id) {
      this.genres = this.genres.includes(id)
        ? this.genres.filter(item => item !== id)
        : [...this.genres, id];
      this.dirty = true;
    },
    next() {
      if (this.canAdvance && this.step < 3) this.step++;
    },
    back() {
      if (this.step > 1) this.step--;
    },
    previewPoster(event) {
      const file = event.target.files[0];
      if (!file) return;
      this.posterName = `${file.name} (${Math.round(file.size / 1024)} KB)`;
      this.posterUrl = URL.createObjectURL(file);
      this.dirty = true;
    },
    beforeUnload(event) {
      if (this.dirty) {
        event.preventDefault();
        event.returnValue = "";
      }
    },
    castJson() {
      return JSON.stringify(this.cast);
    }
  }));

  Alpine.data("genrePicker", () => ({
    search: "",
    open: false
  }));
});

document.addEventListener("DOMContentLoaded", () => {
  Alpine.store("theme").init();
  Alpine.store("watchlist").init();

  // Note: "toast" and "watchlist-updated" events (including HX-Trigger from the server)
  // are handled once, by the @toast.window / @watchlist-updated.window attributes on <body>
  // in base.html. Do not add a second listener here or every toast shows twice.
});
