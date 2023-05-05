from rest_framework import serializers

from apps.hotels.models import Hotel


class HotelSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField()
    country_name = serializers.CharField()

    class Meta:
        model = Hotel
        fields = ('id', 'name', 'stars', 'rating', 'rank', 'reviews', 'description', 'url',
                  'city_name', 'country_name')
