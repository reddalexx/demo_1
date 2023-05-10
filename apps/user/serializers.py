from rest_framework import serializers

from apps.user.models import ContactMe, Subscribe


class ContactMeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactMe
        fields = ('name', 'email', 'subject', 'message')


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ('email',)
