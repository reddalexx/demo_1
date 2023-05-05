from django.conf import settings
from django.db.models import F
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from rest_framework import viewsets

from apps.hotels.forms import HotelsSearchForm
from apps.hotels.models import Hotel
from apps.hotels.serializers import HotelSerializer


class HotelsSearchFormView(FormView):
    template_name = "hotels/search.html"
    form_class = HotelsSearchForm
    success_url = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['is_detail'] = True
        ctx['selected_hotels_url'] = reverse('hotels:selected-hotels')
        return ctx


class OverviewView(TemplateView):
    template_name = 'hotels/overview.html'


class AnalyzeView(TemplateView):
    template_name = 'hotels/analyze.html'


class SelectedHotelsView(TemplateView):
    template_name = 'hotels/selected_hotels.html'


class SelectedHotelsViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ('detail', 'list'):
            qs = qs \
                .select_related('city', 'city__country') \
                .annotate(city_name=F('city__name'),
                          country_name=F('city__country__name'))

        return qs.only('id', 'name', 'stars', 'rank', 'rating', 'reviews', 'description', 'url',
                       'city__name', 'city__country__name')
