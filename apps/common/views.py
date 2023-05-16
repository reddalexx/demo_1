import cachetools.func
import re

from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView


def handler404(request, exception):
    return render(request, 'main/pages/404.html', {})


def handler50x(request, exception=None):
    return render(request, 'main/pages/50x.html', {'status_code': exception.status_code if exception else 500})


class TodoView(TemplateView):
    template_name = 'main/pages/todo.html'
    reg = re.compile(r'\-\s([^\n]+)')

    @cachetools.func.ttl_cache(maxsize=128, ttl=3600)
    def get_todos(self):
        with open(settings.BASE_DIR / 'TODO.md') as f:
            return self.reg.findall(f.read())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['todos'] = self.get_todos()
        return ctx
