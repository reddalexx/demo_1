from django.urls import path, include
from rest_framework import routers

from apps.geo.views import CountryViewSet, CityViewSet, CityListView,CityUpdateView, CountryListView, \
    CountryUpdateView, CountryChartView, CountryCitiesChartView, ChartsView


router = routers.DefaultRouter()
router.register(r'cities', CityViewSet, 'drf-api-city')
router.register(r'countries', CountryViewSet, 'drf-api-country')

urlpatterns = [
    path('api/drf/', include(router.urls)),

    path('cities/', CityListView.as_view(), name='city-list'),
    path(r'cities/<int:pk>/update/', CityUpdateView.as_view(), name='city-update'),

    path('countries/', CountryListView.as_view(), name='country-list'),
    path(r'countries/<int:pk>/update/', CountryUpdateView.as_view(), name='country-update'),

    path(r'charts/', ChartsView.as_view(), name='charts'),
    path('api/drf/country-chart/',
         CountryChartView.as_view(),
         name='drf-api-country-chart'),
    path('api/drf/country-cities-chart/',
         CountryCitiesChartView.as_view(),
         name='drf-api-country-cities-chart'),
]
