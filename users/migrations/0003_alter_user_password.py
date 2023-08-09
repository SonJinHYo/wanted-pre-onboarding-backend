# Generated by Django 4.2 on 2023-08-09 05:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_alter_user_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="password",
            field=models.CharField(
                max_length=128,
                validators=[django.core.validators.MinLengthValidator(8)],
            ),
        ),
    ]
