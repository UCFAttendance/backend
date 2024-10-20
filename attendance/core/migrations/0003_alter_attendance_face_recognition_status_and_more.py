# Generated by Django 4.2.5 on 2023-10-04 02:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attendance",
            name="face_recognition_status",
            field=models.CharField(
                choices=[
                    ("INITIALIZE", "Initialize"),
                    ("PROCESSING", "Processing"),
                    ("SUCCESS", "Success"),
                    ("FAILURE", "Failure"),
                ],
                default="PROCESSING",
                max_length=12,
            ),
        ),
        migrations.AlterField(
            model_name="session",
            name="salt",
            field=models.CharField(default="a55b7302e33543e485c0a821ab9aee71", editable=False, max_length=32),
        ),
    ]
