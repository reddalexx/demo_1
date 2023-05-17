from django.db.models import F, Count
from django.template.exceptions import TemplateDoesNotExist
from django.test import TestCase
from django.urls import reverse

from apps.geo.models import Country, City
from apps.geo.serializers import CountrySerializer
from apps.geo.views import CountryListView, ChartsView, CityListView


class TestCountry(TestCase):
    fixtures = ['demo/data/fixtures/2_countries.json']

    def test_countries_exist(self):
        self.assertTrue(Country.objects.count())

    def test_country_list_template(self):
        url = reverse('geo:country-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, CountryListView.template_name)
        self.assertContains(response, 'Countries')

    def test_country_update(self):
        country = Country.objects.filter(id=1)
        self.assertTrue(country.exists())

        url = reverse('geo:country-update', args=[country.first().id])
        self.assertRaises(TemplateDoesNotExist, self.client.get, url)
        # for now this functional/template doesn't exist

        country_values = country.values()[0]
        new_name = 'FAKE'
        country_values['name'] = new_name
        response = self.client.post(url, data=country_values)
        self.assertRedirects(response, reverse('geo:country-list'), status_code=302,
                             target_status_code=200, fetch_redirect_response=True)
        self.assertEqual(Country.objects.get(pk=1).name, new_name)

    def test_country_list_api(self):
        url = reverse('geo:drf-api-country-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Country.objects.count())
        self.assertDictEqual(response.data[0], CountrySerializer(Country.objects.get(pk=1)).data)

    def test_country_detail_api(self):
        country = Country.objects.get(id=1)
        url = reverse('geo:drf-api-country-detail', kwargs={'pk': country.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, CountrySerializer(country).data)

    def test_country_create_api(self):
        country = Country.objects.filter(id=1)
        country_values = country.values()[0]
        new_name = 'FAKE'
        country_values['name'] = new_name

        url = reverse('geo:drf-api-country-list')
        response = self.client.post(url, data=country_values)
        self.assertEqual(response.status_code, 403)
        # for now API is blocked because it requires authentication class

    def test_country_update_api(self):
        country = Country.objects.get(id=1)
        url = reverse('geo:drf-api-country-detail', kwargs={'pk': country.id})
        response = self.client.patch(url, data={'name', 'FAKE'})
        self.assertEqual(response.status_code, 403)
        # for now API is blocked because it requires authentication class

        response = self.client.put(url, data={'name', 'FAKE'})
        self.assertEqual(response.status_code, 403)
        # for now API is blocked because it requires authentication class

    def test_country_delete_api(self):
        country = Country.objects.get(id=1)
        url = reverse('geo:drf-api-country-detail', kwargs={'pk': country.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        # for now API is blocked because it requires authentication class


class CityTest(TestCase):
    fixtures = ['demo/data/fixtures/2_countries.json', 'demo/data/fixtures/3_cities.json']

    def test_cities_exist(self):
        self.assertTrue(City.objects.count())

    def test_city_list_template(self):
        url = reverse('geo:city-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, CityListView.template_name)
        self.assertContains(response, 'Cities')

    def test_city_update(self):
        city = City.objects.filter(id=1)
        city_values = city.values()[0]

        url = reverse('geo:city-update', args=[city_values['id']])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geo/city_form.html')

        # test wrong form data
        new_name = 'FAKE'
        city_values['name'] = new_name
        response = self.client.post(url, data=city_values)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geo/city_form.html')
        self.assertIn('country', response.context_data['form'].errors)

        # test correct form data
        city_values['country'] = city_values['country_id']
        del city_values['country_id']
        response = self.client.post(url, data=city_values)
        self.assertRedirects(response, reverse('geo:city-list'), status_code=302,
                             target_status_code=200, fetch_redirect_response=True)
        self.assertEqual(City.objects.get(pk=1).name, new_name)

    def test_city_list_api(self):
        url = reverse('geo:drf-api-city-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), City.objects.count())
        self.assertEqual(response.data[0]['name'], City.objects.get(pk=1).name)

    def test_city_detail_api(self):
        city = City.objects.get(id=1)
        url = reverse('geo:drf-api-city-detail', kwargs={'pk': city.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], city.name)

    def test_city_create_api(self):
        city = City.objects.filter(id=1)
        city_values = city.values()[0]
        new_name = 'FAKE'
        city_values['name'] = new_name

        url = reverse('geo:drf-api-city-list')
        response = self.client.post(url, data=city_values)
        self.assertEqual(response.status_code, 403)
        # for now API is blocked because it requires authentication class

    def test_city_update_api(self):
        city = City.objects.get(id=1)
        url = reverse('geo:drf-api-city-detail', kwargs={'pk': city.id})
        response = self.client.patch(url, data={'name', 'FAKE'})
        self.assertEqual(response.status_code, 403)
        # for now API is blocked because it requires authentication class

        response = self.client.put(url, data={'name', 'FAKE'})
        self.assertEqual(response.status_code, 403)
        # for now API is blocked because it requires authentication class

    def test_city_delete_api(self):
        city = City.objects.get(id=1)
        url = reverse('geo:drf-api-city-detail', kwargs={'pk': city.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        # for now API is blocked because it requires authentication class


class ChartsTest(TestCase):
    fixtures = ['demo/data/fixtures/2_countries.json', 'demo/data/fixtures/3_cities.json']

    def test_chart_html_template(self):
        url = reverse('geo:charts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ChartsView.template_name)

    def test_country_chart_by_area_api(self):
        url = reverse('geo:drf-api-country-chart')
        response = self.client.get(url + '?q=area')
        self.assertEqual(response.status_code, 200)
        biggest_country = Country.objects.exclude(population__isnull=True).order_by('-area').first()
        self.assertEqual(response.data['series'][0], biggest_country.area)
        self.assertEqual(response.data['labels'][0], biggest_country.name)
        self.assertIn('colors', response.data)

    def test_country_chart_by_population_api(self):
        url = reverse('geo:drf-api-country-chart')
        response = self.client.get(url + '?q=population')
        self.assertEqual(response.status_code, 200)
        biggest_country = Country.objects.exclude(population__isnull=True).order_by('-population').first()
        self.assertEqual(response.data['series'][0], biggest_country.population)
        self.assertEqual(response.data['labels'][0], biggest_country.name)
        self.assertIn('colors', response.data)

    def test_country_cities_chart_api(self):
        url = reverse('geo:drf-api-country-cities-chart')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        max_cities = Country.objects.annotate(x=F('name'), y=Count('city')).order_by('-y').first()
        self.assertEqual([i for i in response.data['series'][0]['data'] if i['x'] == max_cities.x][0]['y'],
                         max_cities.y)
