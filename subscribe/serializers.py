from rest_framework import serializers
from .models import Subscriber


class SubscriptionSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=200, required=True)

    def create(self, validated_data):
        return Subscriber.objects.create(email=validated_data.get('email'))

    def update(self, instance, validated_data):
        pass