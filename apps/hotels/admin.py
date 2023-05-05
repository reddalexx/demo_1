from django.contrib import admin

from apps.hotels.models import Hotel


class HotelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'stars', 'rating', 'rank', 'reviews', 'uid')
    search_fields = ('name', 'city__name', 'city__county__name', 'city__country__iso3')
    ordering = ['name']

    def city(self, obj):
        return obj.city.name if obj.city else None

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('city')

    city.short_description = 'City'
    city.admin_order_field = 'city'


admin.site.register(Hotel, HotelAdmin)
