from django.views.generic import UpdateView, TemplateView
from django.db.models import F, Sum, Count
from django.urls import reverse

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, views
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.common.utils import get_hex_colors
from apps.geo.models import Country, City
from apps.geo.schemas import CountryChartSchema
from apps.geo.serializers import CitySerializer, CountrySerializer


class CityListView(TemplateView):
    template_name = 'geo/city_list.html'


class CityUpdateView(UpdateView):
    model = City
    fields = '__all__'

    def get_success_url(self):
        return reverse('geo:city-list')


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ('retrieve', 'list'):
            qs = qs.select_related('country').annotate(country_name=F('country__name'), country_iso3=F('country__iso3'))
        return qs


class CityPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class FilterableCityViewSet(CityViewSet):
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'country__name', 'country__iso3']
    search_fields = ['name', 'country__name', 'country__iso3']
    ordering_fields = ['name', 'country__name', 'country__iso3', 'population']
    pagination_class = CityPagination


class CountryListView(TemplateView):
    template_name = 'geo/country_list.html'


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.order_by('name')
    serializer_class = CountrySerializer


class CountryUpdateView(UpdateView):
    model = Country
    fields = '__all__'

    def get_success_url(self):
        return reverse('geo:country-list')


class ChartsView(TemplateView):
    template_name = 'geo/charts.html'


class CountryChartView(views.APIView):
    queryset = Country.objects.exclude(population__isnull=True)
    top_n = 10
    schema = CountryChartSchema()

    def get(self, request, *args, **kwargs):
        target = request.query_params.get('q', 'population')
        if target == 'cities':
            total = self.queryset.count()
            self.queryset = self.queryset.annotate(cities=Count('city'))
        else:
            total = self.queryset.aggregate(s=Sum(target))['s']
        qs = self.queryset.order_by('-' + target)
        top = qs.values_list('name', target)[:self.top_n]
        labels, values = zip(*dict(top).items())
        labels += ('Others',)
        values += (total - sum(values),)
        colors = get_hex_colors(len(values))
        return Response({'labels': labels, 'series': values, 'colors': colors})


class CountryCitiesChartView(views.APIView):
    queryset = Country.objects.exclude(population__isnull=True)
    top_n = 10

    def get(self, request, *args, **kwargs):
        total = self.queryset.count()
        data = list(self.queryset.annotate(x=F('name'), y=Count('city')).order_by('-y').values('x', 'y')[:self.top_n])
        data.append({'x': 'Others', 'y': total - sum([i['y'] for i in data])})
        return Response({'series': [{'data': data[::-1]}]})
