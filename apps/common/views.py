from django.shortcuts import render


def handler404(request, exception):
    return render(request, 'main/pages/404.html', {})


def handler50x(request, exception=None):
    return render(request, 'main/pages/50x.html', {'status_code': request.status_code})
