import os
import redis

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.user.models import ContactMe, Subscribe
from apps.user.serializers import ContactMeSerializer, SubscribeSerializer


r = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'))


class ContactMeView(CreateAPIView):
    queryset = ContactMe.objects.all()
    serializer_class = ContactMeSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        instance = serializer.save()
        if not self.request.user.is_anonymous:
            instance.user = self.request.user
            instance.save()

    def create(self, request, *args, **kwargs):
        cache_key = 'contact_me::' + '::'.join([f'{k}:{v}' for k, v in sorted(list(zip(request.data.keys(), request.data.values())))])
        if r.exists(cache_key):
            return Response(status=status.HTTP_204_NO_CONTENT)
        resp = super().create(request, *args, **kwargs)
        r.set(cache_key, 0, ex=60 * 60 * 24)
        return resp


class SubscribeView(ContactMeView):
    queryset = Subscribe.objects.all()
    serializer_class = SubscribeSerializer
