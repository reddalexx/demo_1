from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from apps.user.models import ContactMe, Subscribe
from apps.user.serializers import ContactMeSerializer, SubscribeSerializer


class ContactMeView(CreateAPIView):
    queryset = ContactMe.objects.all()
    serializer_class = ContactMeSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.user = self.request.user
        instance.save()


class SubscribeView(ContactMeView):
    queryset = Subscribe.objects.all()
    serializer_class = SubscribeSerializer
