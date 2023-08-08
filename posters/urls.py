from django.urls import path
from . import views

urlpatterns = [
    path("", views.Posters.as_view(), name="posters"),
    path("create", views.CreatePosters.as_view(), name="posters_create"),
    path("<int:pk>", views.PosterDetail.as_view(), name="poster_detail"),
]
