from django import forms
from django.core.exceptions import ValidationError
from .models import Movie, Review, CastMember


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["author_name", "rating", "body", "has_spoilers"]
        widgets = {
            "author_name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "rating": forms.HiddenInput(),
            "body": forms.Textarea(attrs={"rows": 5, "maxlength": 500, "placeholder": "Write at least 20 characters..."}),
            "has_spoilers": forms.CheckboxInput(),
        }

    def clean_body(self):
        body = self.cleaned_data["body"].strip()
        if len(body) < 20:
            raise ValidationError("Review must be at least 20 characters.")
        return body


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = [
            "title", "year", "runtime_minutes", "synopsis",
            "poster", "trailer_url", "genres", "is_published"
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Movie title"}),
            "year": forms.NumberInput(attrs={"min": 1900, "max": 2100}),
            "runtime_minutes": forms.NumberInput(attrs={"min": 1}),
            "synopsis": forms.Textarea(attrs={"rows": 6, "maxlength": 2000}),
            "poster": forms.ClearableFileInput(),
            "trailer_url": forms.URLInput(attrs={"placeholder": "https://www.youtube.com/watch?v=..."}),
            "genres": forms.CheckboxSelectMultiple(),
        }


class CastMemberForm(forms.ModelForm):
    class Meta:
        model = CastMember
        fields = ["name", "character"]
