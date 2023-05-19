from django.conf import settings
from django.db.models import Q
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

    def test_list_api_datatables(self):
        url = reverse('hotels:drf-api-hotel-list') + '?format=datatables'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), min(Hotel.objects.count(), settings.REST_FRAMEWORK['PAGE_SIZE'])),
        self.assertEqual(response.data['data'][0]['name'], Hotel.objects.get(pk=response.data['data'][0]['id']).name)

    def test_list_api_datatables_filtering(self):
        search_str = 'Two'
        columns = ['id', 'name', 'city_name', 'country_name', 'description']
        query_str = '&'.join([
            '?format=datatables',
            '&'.join([f'columns[{n}][data]={col}&columns[{n}][searchable]=true' for n, col in enumerate(columns)]),
            f'search[value]={search_str}&search[regex]=false'])
        url = reverse('hotels:drf-api-hotel-list') + query_str
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['recordsTotal'], Hotel.objects.count())
        self.assertEqual(len(response.data['data']), response.data['recordsFiltered'])
        self.assertEqual(
            response.data['recordsFiltered'],
            Hotel.objects.filter(Q(name__icontains=search_str) |
                                 Q(city__name__icontains=search_str) |
                                 Q(city__country__name__icontains=search_str)).count())

    def test_list_api_datatables_ordering(self):
        order_col_name = 'name'
        direction = 'desc'
        columns = ['id', 'name', 'city_name', 'country_name', 'description']
        query_str = '&'.join([
            '?format=datatables',
            '&'.join([f'columns[{n}][data]={col}&columns[{n}][orderable]=true' for n, col in enumerate(columns)]),
            f'order[0][column]={columns.index(order_col_name)}&order[0][dir]={direction}'])
        url = reverse('hotels:drf-api-hotel-list') + query_str
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        expected_total_hotels = Hotel.objects.count()
        self.assertEqual(response.data['recordsTotal'], expected_total_hotels)
        self.assertEqual(response.data['recordsFiltered'], expected_total_hotels)
        self.assertEqual(
            response.data['data'][0][order_col_name],
            getattr(Hotel.objects.order_by(f'{"-" if direction == "desc" else ""}{order_col_name}').first(), order_col_name))

    def test_list_api_datatables_pagination(self):
        order_col_name = 'name'
        direction = 'desc'
        page_offset = 1
        page_size = 1
        columns = ['id', 'name', 'city_name', 'country_name', 'description']
        query_str = '&'.join([
            '?format=datatables',
            '&'.join([f'columns[{n}][data]={col}&columns[{n}][orderable]=true' for n, col in enumerate(columns)]),
            f'order[0][column]={columns.index(order_col_name)}&order[0][dir]={direction}',
            f'start={page_offset}&length={page_size}'
        ])
        url = reverse('hotels:drf-api-hotel-list') + query_str
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        expected_total_hotels = Hotel.objects.count()
        self.assertEqual(response.data['recordsTotal'], expected_total_hotels)
        self.assertEqual(response.data['recordsFiltered'], expected_total_hotels)
        ordering = f'{"-" if direction == "desc" else ""}{order_col_name}'
        self.assertEqual(
            response.data['data'][0][order_col_name],
            getattr(Hotel.objects.order_by(ordering)[page_offset:page_offset+page_size].first(), order_col_name))

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
