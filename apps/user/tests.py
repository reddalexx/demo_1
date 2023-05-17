from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from apps.user.models import ContactMe, Subscribe
from apps.user.views import r


class TestContactMe(TestCase):

    def setUp(self) -> None:
        self.data = {
            'name': 'Test User',
            'email': 'test@email.com',
            'subject': 'Test Subject',
            'message': 'Test Message'
        }
        self.r_key_name = f'{settings.REDIS_KEYS_PREFIX}contact_me::*'
        self.url = reverse('user:contact-me')

    def tearDown(self) -> None:
        for k in r.keys(self.r_key_name):
            r.delete(k)

    def test_api(self):
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContactMe.objects.count(), 1)
        created_subset = {k: v for k, v in ContactMe.objects.values()[0].items() if k in self.data}
        self.assertDictEqual(created_subset, self.data)
        self.assertDictEqual(response.data, self.data)
        self.assertEqual(len(r.keys(self.r_key_name)), 1)

        # test duplicated request
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(ContactMe.objects.count(), 1)
        self.assertEqual(len(r.keys(self.r_key_name)), 1)

    def test_api_wrong_data(self):
        old_name = self.data['name']
        del self.data['name']
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(ContactMe.objects.count(), 0)
        self.assertIn('name', response.data)
        self.assertIn('required', response.data['name'][0])

        self.data['name'] = old_name
        self.data['email'] = 'x'
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(ContactMe.objects.count(), 0)
        self.assertIn('email', response.data)
        self.assertIn('Enter a valid email address', response.data['email'][0])


class TestSubscribe(TestCase):

    def setUp(self) -> None:
        self.data = {
            'email': 'test@email.com',
        }
        self.url = reverse('user:subscribe')

    def test_api(self):
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Subscribe.objects.count(), 1)
        self.assertEqual(Subscribe.objects.get().email, self.data['email'])
        self.assertDictEqual(response.data, self.data)

        # test duplicated request
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Subscribe.objects.count(), 1)
        self.assertIn('email', response.data)
        self.assertIn('already exists', response.data['email'][0])

    def test_api_wrong_data(self):
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Subscribe.objects.count(), 0)
        self.assertIn('email', response.data)
        self.assertIn('required', response.data['email'][0])
