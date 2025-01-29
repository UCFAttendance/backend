# Generated by Django 5.0.11 on 2025-01-28 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('users', '0002_user_init_image'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='user',
            constraint=models.CheckConstraint(check=models.Q(('email__regex', '@ucf.edu')), name='email_whitelisted_domain'),
        ),
    ]
