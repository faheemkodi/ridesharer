# Generated by Django 4.2.3 on 2023-07-07 06:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="mobile_number",
            field=models.CharField(blank=True, default="", max_length=10, unique=True),
        ),
    ]
