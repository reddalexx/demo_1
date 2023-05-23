from django.urls import path, include
from rest_framework import routers

from apps.hotels.views import HotelsSearchFormView, OverviewView, AnalyzeView, SelectedHotelsViewSet, SelectedHotelsView


router = routers.DefaultRouter()
router.register(r'hotels', SelectedHotelsViewSet, 'drf-api-hotel')


urlpatterns = [
    path('api/drf/', include(router.urls)),

    path('selected-hotels/', SelectedHotelsView.as_view(), name='selected-hotels'),
    path('search/', HotelsSearchFormView.as_view(), name='search'),
    path('overview/', OverviewView.as_view(), name='overview'),
    path('analyze/', AnalyzeView.as_view(), name='analyze'),
]
