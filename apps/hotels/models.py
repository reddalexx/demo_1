from django.db import models
from django.db.models.deletion import SET_NULL


class Hotel(models.Model):
    uid = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True, null=True)
    city = models.ForeignKey('geo.City', blank=True, null=True, on_delete=SET_NULL)
    # user = models.ForeignKey('user.User')    # TODO
    rank = models.PositiveIntegerField(blank=True, null=True)
    rank_total = models.PositiveIntegerField(blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    reviews = models.PositiveIntegerField(blank=True, null=True)
    stars = models.PositiveSmallIntegerField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f'{self.name} ({self.stars}) id={self.id}'
