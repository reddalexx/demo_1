"""demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from rest_framework.schemas import get_schema_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('jet/', include('jet.urls', 'jet')),  # Django JET URLS

    path('', TemplateView.as_view(template_name="main/pages/home.html"), name='home'),
    path('about/', TemplateView.as_view(template_name="main/pages/about.html"), name='about'),
    path('architecture/', TemplateView.as_view(template_name="main/pages/architecture.html"), name='architecture'),
    path('features/', TemplateView.as_view(template_name="main/pages/features.html"), name='features'),
    path('team/', TemplateView.as_view(template_name="main/pages/team.html"), name='team'),
    path('quotes/', TemplateView.as_view(template_name="main/pages/quotes.html"), name='quotes'),
    path('contact/', TemplateView.as_view(template_name="main/pages/contact.html"), name='contact'),
    path('404/', TemplateView.as_view(template_name="main/pages/404.html"), name='not_found'),
    path('50x/', TemplateView.as_view(template_name="main/pages/50x.html"), name='error'),

    path('dashboard/', TemplateView.as_view(template_name="dashboard/index.html"), name='dashboard'),

    path('', include(('apps.common.urls', 'common'))),
    path('geo/', include(('apps.geo.urls', 'geo'))),
    path('hotels/', include(('apps.hotels.urls', 'hotels'))),
    path('user/', include(('apps.user.urls', 'user'))),

    path('api/drf/openapi/',
         get_schema_view(title="Demo DRF API", description="DRF API", authentication_classes=[]),
         name='drf-openapi-schema'),
    path('api/drf/swagger/',
         TemplateView.as_view(template_name='swagger/drf.html',
                              extra_context={'schema_url': 'drf-openapi-schema'}),
         name='drf-swagger-ui'),
    path('silk/', include('silk.urls', namespace='silk')),

]

handler404 = 'apps.common.views.handler404'
handler500 = 'apps.common.views.handler50x'
handler503 = 'apps.common.views.handler50x'


if settings.DEBUG is True:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
