from django.test import TestCase
from django.urls import reverse


class TestPages(TestCase):

    def test_main_ui_pages(self):
        pages = (
            ('home', 'home.html', None),
            'about',
            'architecture',
            'features',
            ('team', 'team.html', 'Our Team'),
            'quotes',
            'contact',
            ('not_found', '404.html', '404 Error'),
            ('error', '50x.html', '50x Error'),
            ('common:todo', 'todo.html', 'Todo'),
        )
        for page in pages:
            url_name, template_name, header = page if isinstance(page, tuple) else (page, f'{page}.html', page.capitalize())
            template_name = f'main/pages/{template_name}'
            url = reverse(url_name)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, template_name)
            if header is not None:
                self.assertRegex(response.content.decode('utf-8'), rf'>{header}<')

    def test_dashboard_ui_pages(self):
        pages = (
            ('dashboard', 'dashboard/index.html', 'Dashboard Analytics'),
        )
        for url_name, template_name, header in pages:
            url = reverse(url_name)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, template_name)
            if header is not None:
                self.assertRegex(response.content.decode('utf-8'), rf'>{header}<')

    def test_drf_swagger_ui(self):
        url = reverse('drf-swagger-ui')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'swagger/drf.html')
        self.assertIn('DRF Swagger', response.content.decode('utf-8'))

        url = reverse('drf-openapi-schema')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['info']['title'], 'Demo DRF API')
        self.assertEqual(response.data['info']['version'], '1.0.0')

    def test_404(self):
        response = self.client.get('fake')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/pages/404.html')

    def test_silky_ui(self):
        url = reverse('silk:summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Silky', response.content.decode('utf-8'))
