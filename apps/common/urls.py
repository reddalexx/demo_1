from django.urls import path

from apps.common.views import TodoView


urlpatterns = [
    path(r'todo/', TodoView.as_view(), name='todo'),
]
