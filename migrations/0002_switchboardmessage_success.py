# Generated by Django 4.2.16 on 2024-12-02 16:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("oas", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="switchboardmessage",
            name="success",
            field=models.BooleanField(default=False),
        ),
    ]
