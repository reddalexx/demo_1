# Generated by Django 4.1.7 on 2023-04-05 09:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100)),
                ('iso3', models.CharField(db_index=True, max_length=3)),
                ('population', models.PositiveIntegerField(blank=True, null=True)),
                ('area', models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Countries',
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100)),
                ('is_capital', models.BooleanField(default=False)),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('population', models.PositiveIntegerField(blank=True, null=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='geo.country')),
            ],
            options={
                'verbose_name_plural': 'Cities',
            },
        ),
    ]
