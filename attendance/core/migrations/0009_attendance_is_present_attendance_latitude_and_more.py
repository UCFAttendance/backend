# Generated by Django 5.0.11 on 2025-02-06 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_session_face_recognition_enabled_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='is_present',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='attendance',
            name='latitude',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='longitude',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='session',
            name='latitude',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='session',
            name='longitude',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='face_recognition_status',
            field=models.CharField(choices=[('NOT_REQUIRED', 'Not Required'), ('PENDING', 'Pending'), ('SUCCESS', 'Success'), ('FAILED', 'Failed')], default='NOT_REQUIRED', max_length=12),
        ),
    ]
