from django.contrib import admin

from apps.geo.models import Country, City


class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'iso3', 'population', 'area')
    search_fields = ('name', 'iso3')
    ordering = ['name']


class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country', 'is_capital', 'lat', 'lng', 'population')
    search_fields = ('name', 'country__name', 'country__iso3')
    ordering = ['name']

    def country(self, obj):
        return obj.country.name

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('country')

    country.short_description = 'Country'
    country.admin_order_field = 'country'


admin.site.register(Country, CountryAdmin)
admin.site.register(City, CityAdmin)
