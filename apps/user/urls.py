from django.urls import path
from rest_framework import routers

from apps.user.views import ContactMeView, SubscribeView


# router = routers.DefaultRouter()
# router.register('contact-me', ContactMeView)
# router.register('subscribe',SubscribeView)


urlpatterns = [
    path('api/drf/contact-me/', ContactMeView.as_view(), name='contact-me'),
    path('api/drf/subscribe/', SubscribeView.as_view(), name='subscribe'),
]
