from rest_framework import serializers
from rest_framework.exceptions import ValidationError, ErrorDetail
from django.utils.translation import ugettext_lazy as _


class PaymentSerializer(serializers.Serializer):
    public_id = serializers.UUIDField(required=True)
    quant = serializers.IntegerField(required=True)
    is_vip = serializers.BooleanField(default=False, required=False)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def validate_quantity(self, value):
        if value <= 0:
            raise ValidationError(_("Quantity should be at least 1."))


class TicketCreateSerializer(serializers.Serializer):
    refund_id = serializers.CharField(max_length=100, required=False)
    payment_id = serializers.IntegerField(required=True)
    is_ok = serializers.BooleanField(default=False, allow_null=True)

    def to_internal_value_one_value(self, data, field):

        get_field = self.get_fields().get(field)
        try:
            primitive_value = get_field.to_internal_value(data)
        except Exception as e:
            return None
        return primitive_value

    def is_valid(self, *args, **kwargs):
        super(TicketCreateSerializer, self).is_valid(*args, **kwargs)
        if not self._errors:
            self._errors = {}
        if not self._errors.get('is_ok') or not self._errors.get('refund_id'):
            is_ok = self.to_internal_value_one_value(self.initial_data.get('is_ok'), 'is_ok')
            refund_id = self.to_internal_value_one_value(self.initial_data.get('refund_id'), 'refund_id')
            if is_ok is not None and is_ok:
                if not refund_id:
                    self._errors['refund_id'] = [
                        ErrorDetail(string="Refund Id is required for is_ok true.",
                                    code='invalid')]
            elif is_ok is None:
                self._errors['is_ok'] = [
                    ErrorDetail(string="This field is required.",
                                code='invalid')]
        return bool(not self._errors)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

class TicketUpdateSerializer(serializers.Serializer):
    public_id = serializers.IntegerField(required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

