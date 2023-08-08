from django.urls import path
from . import views

urlpatterns = [
    path("create", views.Posters.as_view(), name="posters"),
]
