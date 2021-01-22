import uuid

from rest_framework import serializers

from authentication.serializers import error_many_list_serializer
from event_crud.errors import EventShouldHaveAtLeastOneCategory
from main_app.api_exceptions import InstanceDoesNotHaveCategory, SessionAlreadyExpired
from main_app.constants import RESET_PASSWORD_ATTEMPTS
from user_crud.models import CustomUser, Category, Address
from user_crud.utils import uuid_hash
from authentication.errors import ValidationError, ValidationErrorBase
from authentication.models import Session


class UserRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(max_length=200, required=True)
    password = serializers.CharField(max_length=200, required=True)
    phone_number = serializers.CharField(max_length=100, required=True)
    gender = serializers.ChoiceField(choices=["M", "Male", "F", "Female", "O", "Other"], required=False)
    is_termsandconditions_accepted = serializers.BooleanField()
    birth_date = serializers.DateField(default=None, required=False)
    is_company = serializers.BooleanField(default=False)

    def create(self, validated_data):
        return CustomUser.objects.create_user(validated_data)

    def update(self, instance, validated_data):
        pass


class CompanyRegistrationSerializer(UserRegistrationSerializer):
    name = serializers.CharField(max_length=200, required=True)


class UserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    phone_number = serializers.CharField(max_length=100, required=False)
    gender = serializers.ChoiceField(choices=["M", "Male", "F", "Female", "O", "Other"], required=False)
    birth_date = serializers.DateField(required=False)
    name = serializers.CharField(max_length=200, required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        return instance.update(validated_data)


class CategorySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=True)
    description = serializers.CharField(max_length=500, required=False)

    def create(self, validated_data):
        return Category.objects.create(validated_data)

    def update(self, instance, validated_data):
        pass


class CategoryUserSerializer(serializers.Serializer):
    categories = CategorySerializer(many=True)
    user = None
    event = None

    def __init__(self, event = None, user=None, *args, **kwargs):
        self.event = event
        self.user = user
        super(CategoryUserSerializer, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        category_data = validated_data.pop('categories')
        for single_category in category_data:
            try:
                category = Category.objects.get(name=single_category.get("name"))
                instance.categories.add(category)
            except (Category.DoesNotExist, Category.MultipleObjectsReturned):
                pass

    def remove(self, instance, validated_data):
        category_data = validated_data.pop('categories')
        for single_category in category_data:
            try:
                category = Category.objects.get(name=single_category.get("name"))
                if instance.categories.filter(name=category.name):
                    if self.event:
                        if not instance.categories.count()>=2:
                            raise EventShouldHaveAtLeastOneCategory()
                    instance.categories.remove(category)
            except (Category.DoesNotExist, Category.MultipleObjectsReturned):
                pass

# add address region
class AddressSerializer(serializers.Serializer):
    address1 = serializers.CharField(max_length=100, required=True)
    address2 = serializers.CharField(max_length=100, required=True)
    city = serializers.CharField(max_length=100, required=True)
    state = serializers.CharField(max_length=100, required=True)
    country = serializers.CharField(max_length=100, required=True)

    def create(self, validated_data):
        return Address.objects.create(validated_data)

    @staticmethod
    def get_hash(validated_data):
        return uuid_hash(**validated_data)

    def update(self, instance, validated_data):
        return instance.update(validated_data)


class ResetPasswordSerializer(serializers.Serializer):

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    old_password = serializers.CharField(max_length=128, required=True)
    password1 = serializers.CharField(max_length=128, required=True)
    password2 = serializers.CharField(max_length=128, required=True)
    session = None

    def __init__(self, session = None, *args, **kwargs):
        self.session = session
        super(ResetPasswordSerializer, self).__init__(*args, **kwargs)

    def validate_passwords(self, user):
        if self.is_valid():
            if user.check_password(self.validated_data.get('old_password')):
                if not self.validated_data.get('password1') == self.validated_data.get('password2'):
                    raise ValidationErrorBase(field="password2", message='Passwords do not match.')
                user.set_password(self.validated_data.get('password1'))
                user.reset_password_attempts = 0
                user.save()
                return
            user.reset_password_attempts += 1
            user.save()
            # todo check this
            if user.reset_password_attempts == RESET_PASSWORD_ATTEMPTS:
                user.reset_password_attempts = 0
                self.session.expire_session()
                raise SessionAlreadyExpired
            raise ValidationErrorBase(field="old_password", message='Provided password is incorrect.')
        raise ValidationError(error_list=error_many_list_serializer(self.errors))