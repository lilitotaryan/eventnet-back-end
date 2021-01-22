from rest_framework import serializers

from authentication.errors import ValidationErrorBase


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100, required=True)
    password = serializers.CharField(max_length=200, required=True)
    device_brand = serializers.CharField(max_length=200, required=False)
    os_system = serializers.CharField(max_length=200, required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserEmailValidationTokenSerializer(serializers.Serializer):
    token = serializers.UUIDField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    @staticmethod
    def check_token(instance, validated_data):
        return instance.get_verification_token() == validated_data.get("token")


class ForgotPasswordSerializer(serializers.Serializer):

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    password1 = serializers.CharField(max_length=128, required=True)
    password2 = serializers.CharField(max_length=128, required=True)

    def validate(self, data):
        if not data.get('password1') == data.get('password2'):
            error = serializers.ValidationError(
                'Passwords do not match.'
            )
            raise error
        return super(ForgotPasswordSerializer, self).validate(data)


def validation_error_generator(e, prev_e="", index=-1):
    error = ValidationErrorBase()
    error.field = "{}_{}_{}".format(prev_e, e[0], index) if index>=0 and prev_e else e[0]
    error.message = str(e[1][0])
    return error


def error_many_list_serializer(error_dict):
    errors = []
    for e in error_dict.items():
        _, error_items = e
        if isinstance(error_items, dict):
            for e_item in error_items.items():
                errors.append(validation_error_generator(e_item))
        elif isinstance(error_items, list) and isinstance(error_items[0], dict):
            for e_item in range(0, len(error_items)):
                for e in error_items[e_item].items():
                    errors.append(validation_error_generator(e, _, e_item))
        else:
            errors.append(validation_error_generator(e))
    return errors
