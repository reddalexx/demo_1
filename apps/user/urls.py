from django.urls import path

from apps.user.views import ContactMeView, SubscribeView


urlpatterns = [
    path('api/drf/contact-me/', ContactMeView.as_view(), name='contact-me'),
    path('api/drf/subscribe/', SubscribeView.as_view(), name='subscribe'),
]
