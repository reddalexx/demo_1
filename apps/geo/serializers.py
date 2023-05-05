from rest_framework import serializers

from apps.geo.models import Country, City


class CitySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField()
    country_iso3 = serializers.CharField()

    class Meta:
        model = City
        fields = ('id', 'name', 'country_name', 'country_iso3', 'lat', 'lng', 'population')


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = '__all__'
