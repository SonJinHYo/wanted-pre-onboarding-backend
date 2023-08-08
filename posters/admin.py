from django.contrib import admin
from .models import Poster


@admin.register(Poster)
class PosterAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "created_at",
    )
