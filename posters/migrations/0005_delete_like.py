# Generated by Django 4.2 on 2023-08-10 03:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("posters", "0004_alter_poster_created_at_alter_poster_updated_at_like"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Like",
        ),
    ]
