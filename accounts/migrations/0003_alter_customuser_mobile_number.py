# Generated by Django 4.2.3 on 2023-07-07 06:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_alter_customuser_mobile_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="mobile_number",
            field=models.CharField(blank=True, default="", max_length=10),
        ),
    ]