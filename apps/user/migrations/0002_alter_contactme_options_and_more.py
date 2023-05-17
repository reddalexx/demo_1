# Generated by Django 4.1.7 on 2023-05-16 15:42

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contactme',
            options={'verbose_name_plural': 'Contact Me'},
        ),
        migrations.AlterUniqueTogether(
            name='subscribe',
            unique_together={('user', 'email')},
        ),
    ]