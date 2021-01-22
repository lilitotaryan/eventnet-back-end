from datetime import timedelta
from django.utils.translation import ugettext_lazy as _
from authentication.utils import get_current_date, get_current_time
from event_crud.errors import EventDateNotValid, EventAlreadyExists
from main_app.api_exceptions import CompanyNotFound
from main_app.constants import EVENT_DAY_INTERVAL, EVENT_START_END_INTERVAL
from user_crud.serializers import CategorySerializer, AddressSerializer, AddressSerializer, UserRegistrationSerializer
from rest_framework import serializers
from user_crud.models import CustomUser, Address, Category
from user_crud.utils import uuid_hash
from .models import Event
from django.db import IntegrityError
import re

from collections import OrderedDict
from collections.abc import Mapping


from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.fields import get_error_detail, set_value
from rest_framework.settings import api_settings

from rest_framework.fields import SkipField

class EventCompanyUser(serializers.Serializer):
    name = serializers.CharField(max_length=200, required=True)
    user = None

    def to_internal_value_one_value(self, data, field):

        get_field = self.get_fields().get(field)
        primitive_value = get_field.to_internal_value(data)

        return primitive_value

    def validate_name(self, value):
        user = CustomUser.objects.filter(name=value).first()
        if not user:
            raise ValidationError(_("There is no registered company with specified name {}.".format(value)))
        self.user = user

    # def is_valid(self, *args, **kwargs):
    #     super(EventCompanyUser, self).is_valid(*args, **kwargs)
    #     if not self._errors:
    #         self._errors = {}
    #     if not self._errors.get('name'):
    #         name = self.to_internal_value_one_value(self.initial_data.get('name'), 'name')
    #         if name:
    #             user = CustomUser.objects.filter(name=name).first()
    #             self.user = user
    #         else:
    #             self._errors['name'] = [
    #                      ErrorDetail(string="There is no registered company with specified name",
    #                                         code='invalid')]
    #     return bool(not self._errors)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        if self.user:
            instance.users.add(self.user)


class EventCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, required=True)
    description = serializers.CharField(max_length=500, required=True)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    is_responsible = serializers.BooleanField(required=False)
    contact_phone_number = serializers.CharField(max_length=100, required=True)
    categories = CategorySerializer(many=True, required=False)
    address = AddressSerializer(required=True)
    users = EventCompanyUser(many=True, required=False)
    ticket_amount = serializers.IntegerField(required=True)
    ticket_fee = serializers.IntegerField(default=0)
    vip_ticket_fee = serializers.IntegerField(default=0)

    def to_internal_value_one_value(self, data, field):

        get_field = self.get_fields().get(field)
        primitive_value = get_field.to_internal_value(data)

        return primitive_value

    def is_valid(self, *args, **kwargs):
        super(EventCreateSerializer, self).is_valid(*args, **kwargs)
        exp_day, exp_hour, exp_min, exp_sec = EVENT_DAY_INTERVAL
        exp_day_se, exp_hour_se, exp_min_se, exp_sec_se = EVENT_START_END_INTERVAL
        if not self._errors:
            self._errors = {}
        if not self.initial_data.get('start_date'):
            self._errors['start_date'] = [
                ErrorDetail(string="This field may not be blank.",
                            code='invalid')]
        if not self.initial_data.get('end_date'):
            self._errors['end_date'] = [
                ErrorDetail(string="This field may not be blank.",
                            code='invalid')]
        if not self._errors.get('start_date'):
            start_date = self.to_internal_value_one_value(self.initial_data.get('start_date'), 'start_date')
            if start_date:
                if start_date <= get_current_time():
                    self._errors['start_date'] = [
                         ErrorDetail(string="Start date should be bigger than now.",
                                            code='invalid')]
                if not self._errors.get('start_date') and start_date < get_current_time() + timedelta(days=exp_day,
                                                                                                  hours=exp_hour,
                                                                                                  minutes=exp_min,
                                                                                                  seconds=exp_sec):
                    self._errors['start_date'] = [
                         ErrorDetail(string="We require at least: {}, hours: {}, minutes: {}, "
                                            "seconds: {} for promotion of the event.".format(exp_day, exp_hour, exp_min, exp_sec),
                                            code='invalid')]
                end_date = self.to_internal_value_one_value(self.initial_data.get('end_date'), 'end_date')
                if end_date:
                    if start_date > end_date:
                        self._errors['end_date'] = [ErrorDetail(string='End date cannot be lower than start date.', code='invalid')]
                    if not self._errors.get('end_date') and end_date < start_date + \
                                timedelta(days=exp_day_se, hours=exp_hour_se, minutes=exp_min_se, seconds=exp_sec_se):
                            self._errors['end_date'] = [ErrorDetail(string="End date should have a least days: {}, hours: {}, minutes: {}, "
                                                                     "seconds: {} interval compared to start date.".format(exp_day_se,
                                                                                                                           exp_hour_se,
                                                                                                                           exp_min_se,
                                                                                                                           exp_sec_se),
                                                              code='invalid')]
        return bool(not self._errors)

    # todo add date part into models find all parts that may be changed from admin and cause error
    def create(self, validated_data):
        address_data = validated_data.pop('address')
        users_data = validated_data.pop('users', None)
        categories_data = validated_data.pop('categories', None)
        address = Address.objects.filter(hash=uuid_hash(**address_data)).first()
        if not address:
            address = Address.objects.create(address_data)
        validated_data['address'] = address
        try:
            event = Event.objects.create(**validated_data)
        except IntegrityError as e:
            raise EventAlreadyExists()
        if users_data:
            for i in users_data:
                company = CustomUser.objects.filter(name=i.get('name')).first()
                if company:
                    event.users.add(company)
        if categories_data:
            for i in categories_data:
                category = Category.objects.filter(name=i.get('name')).first()
                if category:
                    event.categories.add(category)
        return event

    def update(self, instance, validated_data):
        pass


class EventUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, required=False)
    description = serializers.CharField(max_length=500, required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    ticket_amount = serializers.IntegerField(default=0, required=False)
    contact_phone_number = serializers.CharField(max_length=100, required=False)
    event = None

    def __init__(self, event = None, *args, **kwargs):
        self.event = event
        super(EventUpdateSerializer, self).__init__(*args, **kwargs)

    def to_internal_value_one_value(self, data, field):

        get_field = self.get_fields().get(field)
        primitive_value = get_field.to_internal_value(data)

        return primitive_value

    def create(self, validated_data):
        pass

    def is_valid(self, *args, **kwargs):
        super(EventUpdateSerializer, self).is_valid(*args, **kwargs)
        exp_day, exp_hour, exp_min, exp_sec = EVENT_DAY_INTERVAL
        exp_day_se, exp_hour_se, exp_min_se, exp_sec_se = EVENT_START_END_INTERVAL
        if not self._errors:
            self._errors = {}
        if not self.initial_data.get('start_date'):
            self._errors['start_date'] = [
                ErrorDetail(string="This field may not be blank.",
                            code='invalid')]
        if not self.initial_data.get('end_date'):
            self._errors['end_date'] = [
                ErrorDetail(string="This field may not be blank.",
                            code='invalid')]
        if not self._errors.get('start_date') and self.initial_data.get('start_date'):
            start_date = self.to_internal_value_one_value(self.initial_data.get('start_date'), 'start_date')
            if start_date:
                if start_date <= get_current_time():
                    self._errors['start_date'] = [
                         ErrorDetail(string="Start date should be bigger than now.",
                                            code='invalid')]

                if not self._errors.get('start_date') and (self.event.start_date - self.event.creation_date) + \
                        (start_date - get_current_time()) <\
                        timedelta(days=exp_day,
                                                                                                  hours=exp_hour,
                                                                                                  minutes=exp_min,
                                                                                                  seconds=exp_sec):
                    self._errors['start_date'] = [
                         ErrorDetail(string="We require at least: {}, hours: {}, minutes: {}, "
                                            "seconds: {} for promotion of the event.".format(exp_day, exp_hour, exp_min, exp_sec),
                                            code='invalid')]
                if self.initial_data.get('end_date'):
                    end_date = self.to_internal_value_one_value(self.initial_data.get('end_date'), 'end_date')
                else:
                    end_date = self.event.end_date
                if end_date:
                    if start_date > end_date:
                        self._errors['end_date'] = [ErrorDetail(string='End date cannot be lower than start date.', code='invalid')]
                    if not self._errors.get('end_date') and end_date < start_date + \
                                    timedelta(days=exp_day_se, hours=exp_hour_se, minutes=exp_min_se, seconds=exp_sec_se):
                                self._errors['end_date'] = [ErrorDetail(string="End date should have a least days: {}, hours: {}, minutes: {}, "
                                                                         "seconds: {} interval compared to start date.".format(exp_day_se,
                                                                                                                               exp_hour_se,
                                                                                                                               exp_min_se,
                                                                                                                               exp_sec_se),
                                                                  code='invalid')]

        elif self.initial_data.get('end_date'):
            end_date = self.to_internal_value_one_value(self.initial_data.get('end_date'), 'end_date')
            start_date = self.event.start_date
            if end_date:
                if start_date > end_date:
                    self._errors['end_date'] = [
                        ErrorDetail(string='End date cannot be lower than start date.', code='invalid')]
                if not self._errors.get('end_date') and end_date < start_date + \
                        timedelta(days=exp_day_se, hours=exp_hour_se, minutes=exp_min_se, seconds=exp_sec_se):
                    self._errors['end_date'] = [
                        ErrorDetail(string="Start date should be at least days: {}, hours: {}, minutes: {}, "
                                           "seconds: {} earlier compared to end date.".format(exp_day_se,
                                                                                                 exp_hour_se,
                                                                                                 exp_min_se,
                                                                                                 exp_sec_se),
                                    code='invalid')]
        return bool(not self._errors)

    # todo change/complete this
    def update(self, instance, validated_data):
        instance.update(validated_data)
        return instance


class EventFilterSerializer(serializers.Serializer):
    categories = serializers.ListField(required = False)
    states = serializers.ListField(required = False)
    cities = serializers.ListField(required = False)
    start_date = serializers.IntegerField(default=2)
    ticket_fee = serializers.IntegerField(default=2)
    free = serializers.BooleanField(required = False)
    is_responsible = serializers.BooleanField(required = False)

# todo check for boolean
    def validate(self, data):
        data['categories'] = [re.sub(r"[^a-zA-Z]","", i) for i in data['categories']]
        data['states'] = [re.sub(r"[^a-zA-Z]", "", i) for i in data['states']]
        data['cities'] = [re.sub(r"[^a-zA-Z]", "", i) for i in data['cities']]
        return data


class FreeTicketCreateSerializer(serializers.Serializer):
    quant = serializers.IntegerField(required=True)
    is_vip = serializers.BooleanField(default=False, required=False)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def validate_quantity(self, value):
        if value <= 0:
            raise ValidationError(_("Quantity should be at least 1."))