# Generated by Django 4.2 on 2023-08-08 06:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("posters", "0002_alter_poster_created_at_alter_poster_updated_at"),
    ]

    operations = [
        migrations.RenameField(
            model_name="content",
            old_name="content",
            new_name="text",
        ),
        migrations.DeleteModel(
            name="Like",
        ),
    ]