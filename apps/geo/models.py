from django.db import models
from django.db.models.deletion import CASCADE


class Country(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    iso3 = models.CharField(max_length=3, db_index=True)
    population = models.PositiveIntegerField(blank=True, null=True)
    area = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Countries'

    def __str__(self):
        return f'{self.name} ({self.iso3}) id={self.id}'


class City(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    country = models.ForeignKey(Country, db_index=True, on_delete=CASCADE)
    is_capital = models.BooleanField(default=False)
    lat = models.FloatField()
    lng = models.FloatField()
    population = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Cities'

    def __str__(self):
        return f'{self.name} ({self.country.iso3}) id={self.id}'
