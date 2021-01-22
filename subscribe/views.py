from django.shortcuts import render
from rest_framework.views import APIView

from authentication.serializers import error_many_list_serializer
from authentication.utils import response
from authentication.errors import ValidationError
from .serializers import SubscriptionSerializer

# Create your views here.
from authentication.permissions import ApiTokenPermission


class SubscriptionView(APIView):
    permission_classes = [ApiTokenPermission]

    def post(self, request):
        data = SubscriptionSerializer(data=request.data)
        if data.is_valid():
            data.create(data.validated_data)
            return response()
        raise ValidationError(error_list=error_many_list_serializer(data.errors))

