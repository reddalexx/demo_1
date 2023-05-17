from django.test import TestCase
from django.urls import reverse

from mixer.backend.django import mixer

from apps.geo.models import City
from apps.hotels.models import Hotel


class TestPages(TestCase):
    fixtures = ['demo/data/fixtures/2_countries.json', 'demo/data/fixtures/3_cities.json']

    def test_app_pages(self):
        pages = (
            ('hotels:overview', 'hotels/overview.html', 'Overview'),
            ('hotels:search', 'hotels/search.html', 'Search'),
            ('hotels:analyze', 'hotels/analyze.html', 'Test and Analyze'),
            ('hotels:selected-hotels', 'hotels/selected_hotels.html', 'Selected Hotels'),
        )
        for url_name, template_name, header in pages:
            url = reverse(url_name)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, template_name)
            if header is not None:
                self.assertRegex(response.content.decode('utf-8'), rf'>{header}<')


class TestSelectedHotelsAPI(TestCase):
    fixtures = ['demo/data/fixtures/2_countries.json', 'demo/data/fixtures/3_cities.json']

    def setUp(self) -> None:
        self.hotel_1 = mixer.blend(Hotel, name='Hotel One', city=City.objects.first())
        self.hotel_2 = mixer.blend(Hotel, name='Hotel Two', city=City.objects.last())

    def test_list_api(self):
        url = reverse('hotels:drf-api-hotel-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Hotel.objects.count())
        self.assertEqual(response.data[0]['name'], Hotel.objects.get(pk=response.data[0]['id']).name)

    def test_detail_api(self):
        hotel = Hotel.objects.first()
        url = reverse('hotels:drf-api-hotel-detail', kwargs={'pk': hotel.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], hotel.name)

    def test_detail_api_wrong_id(self):
        url = reverse('hotels:drf-api-hotel-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_create_api(self):
        hotel = Hotel.objects.filter(id=self.hotel_1.id)
        hotel_values = {k: v for k, v in hotel.values()[0].items() if v}
        hotel_values['uid'] = 9999

        url = reverse('hotels:drf-api-hotel-list')
        response = self.client.post(url, data=hotel_values)
        self.assertEqual(response.status_code, 403)
        # for now API is blocked because it requires authentication class

    def test_update_api(self):
        hotel = Hotel.objects.first()
        url = reverse('hotels:drf-api-hotel-detail', kwargs={'pk': hotel.id})
        response = self.client.patch(url, data={'name', 'FAKE'})
        self.assertEqual(response.status_code, 403)
        # for now API is blocked because it requires authentication class

        response = self.client.put(url, data={'name', 'FAKE'})
        self.assertEqual(response.status_code, 403)
        # for now API is blocked because it requires authentication class

    def test_delete_api(self):
        hotel = Hotel.objects.first()
        url = reverse('hotels:drf-api-hotel-detail', kwargs={'pk': hotel.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        # for now API is blocked because it requires authentication class
