# Generated by Django 4.1.7 on 2023-05-17 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_contactme_options_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='subscribe',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='subscribe',
            name='email',
            field=models.EmailField(db_index=True, max_length=254, unique=True),
        ),
    ]
