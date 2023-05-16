from django.contrib.auth.models import User
from django.db import models
from django.db.models.deletion import SET_NULL


class ContactMe(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=SET_NULL)
    name = models.CharField(max_length=200, db_index=True)
    email = models.EmailField(db_index=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    reviewed = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name_plural = 'Contact Me'

    def __str__(self):
        return f'{self.date}: {self.email} ({self.reviewed})'


class Subscribe(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=SET_NULL)
    email = models.EmailField(db_index=True)
    subscribed = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = ('user', 'email')

    def __str__(self):
        return f'{self.date}: {self.email} ({self.subscribed})'
