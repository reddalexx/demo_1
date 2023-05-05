from django import forms

from apps.geo.models import City


def get_city_choices():
    return [(n, i) for n, i in City.objects.order_by('name').values_list('id', 'name')]


def get_initial_city():
    city = City.objects.filter(name='Dubai')
    if city.exists:
        return city.get().id
    return City.objects.order_by('id').first().id


class HotelsSearchForm(forms.Form):
    city = forms.ChoiceField(choices=get_city_choices, initial=get_initial_city)
    page = forms.IntegerField(initial=1)
