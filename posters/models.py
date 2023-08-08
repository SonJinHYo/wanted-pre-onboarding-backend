from django.db import models


class Poster(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="posters",
    )
    title = models.CharField(max_length=50)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


class Content(models.Model):
    poster = models.OneToOneField(
        "posters.Poster",
        on_delete=models.CASCADE,
        related_name="contents",
    )
    text = models.TextField(max_length=1000)


class Like(models.Model):
    poster = models.ForeignKey(
        "posters.Poster",
        on_delete=models.CASCADE,
        related_name="likes",
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="likes",
    )
