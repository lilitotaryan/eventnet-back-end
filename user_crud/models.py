import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models, IntegrityError

from user_crud.errors import UserAlreadyExists, AddressAlreadyExists, CompanyUserShouldHaveName
from authentication.utils import get_current_time
from main_app.constants import VERIFICATION_TOKEN_EXPIRATION_TIME, OT_TOKEN_EXPIRATION_TIME
from user_crud.utils import uuid_hash


def generate_int_token():
    return uuid.uuid4().int % 10000

class Category(models.Model):
    name = models.CharField(max_length=100, blank=False, default=None, unique=True)
    description = models.CharField(max_length=500, blank=True)

    def serialize(self):
        return {"name": self.name,
                "description": self.description
                }

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class AddressManager(models.Manager):
    def create(self, obj_data):
        address_hash = uuid_hash(**obj_data)
        obj_data["hash"] = address_hash
        return super().create(**obj_data)


class Address(models.Model):
    address1 = models.CharField(max_length=100, blank=False, default=None)
    address2 = models.CharField(max_length=100, blank=True, default="")
    city = models.CharField(max_length=100, blank=False, default=None)
    state = models.CharField(max_length=100, blank=False, default=None)
    country = models.CharField(max_length=100, blank=False, default=None)
    hash = models.UUIDField(unique=True, blank=False, default=None)
    objects = AddressManager()

    def __str__(self):
        return f"Street:{self.address1} Apt:{self.address2}"

    def serialize(self):
        return {"address1": self.address1,
                "address2": self.address2,
                "city": self.city,
                "state": self.state,
                "country": self.country}

    def update(self, other):
        self.address1 = other.get("address1") if other.get("address1") else self.address1
        self.address2 = other.get("address2") if other.get("address2") else self.address2
        self.city = other.get("city") if other.get("city") else self.city
        self.state = other.get("state") if other.get("state") else self.state
        self.country = other.get("country") if other.get("country") else self.country
        # self.hash = other.get("hash") if other.get("hash") else uuid_hash(self.address1, self.city,
        #                                                                   self.address2, self.state)
        try:
            self.save()
        except IntegrityError:
            raise AddressAlreadyExists()
        return self

    class Meta:
        verbose_name_plural = "Addresses"


class CustomUserManager(UserManager):

    def _create_user(self, **other):
        is_company = other.get('is_company')
        password = other.get('password')
        user = self.model(**other)
        user.set_password(password)
        if is_company and not other.get('name'):
            raise CompanyUserShouldHaveName()
        try:
            user.save(using=self._db)
        except IntegrityError:
            raise UserAlreadyExists()
        return user

    def create_user(self, other):
        other.setdefault('is_staff', False)
        other.setdefault('is_superuser', False)
        return self._create_user(**other)

    def create_superuser(self, other):
        other.setdefault('is_staff', True)
        other.setdefault('is_superuser', True)

        if other.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if other.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(**other)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(max_length=200, blank=False, default=None, unique=True)
    password = models.CharField(max_length=200, blank=False, default=None)
    phone_number = models.CharField(max_length=100, blank=False, default=None, unique=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.CharField(max_length=6, default="F", choices=[("M", "Male"),
                                                                  ("F", "Female"),
                                                                  ("O", "Other")])
    is_verified = models.BooleanField(default=False)
    is_termsandconditions_accepted = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=get_current_time)
    name = models.CharField(max_length=200, default=None, unique=True, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True, default=None)
    ot_token = models.IntegerField(default=generate_int_token, unique=True)
    ot_token_date = models.DateTimeField(default=get_current_time)
    is_company = models.BooleanField(default=False)
    verification_token = models.UUIDField(unique=True, blank=False, default=uuid.uuid4)
    verification_token_time = models.DateTimeField(default=get_current_time)
    reset_password_attempts = models.IntegerField(default=0)
    categories = models.ManyToManyField(Category, blank=True)
    stripe_id = models.CharField(max_length=200, null=True, blank=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def serialize(self, extra_info = False):
        res = {"first_name": self.first_name,
               "last_name": self.last_name,
               "phone_number": self.phone_number,
               "email": self.email,
               "name": self.name if self.is_company else "",
               "stripe_id": self.stripe_id
               }
        if extra_info:
            res["gender"] = self.gender
            res["birth_date"]= self.birth_date
            res["address"]= self.address.serialize() if self.address else ""
            res["is_verified"] = self.is_verified
            res["is_termsandconditions_accepted"] = self.is_termsandconditions_accepted
            res["is_company"] = self.is_company
            res["name"] = self.name if self.is_company else ""
            if not self.is_company:
                res["category"] = [category.serialize() for category in self.categories.all()] if self.categories else []
        return res

    def update(self, other):
        self.phone_number = other.get("phone_number") if other.get("phone_number") else self.phone_number
        self.gender = other.get("gender") if other.get("gender") else self.gender
        self.name = other.get("name") if other.get("name") else self.name
        self.birth_date = other.get("birth_date") if other.get("birth_date") else self.birth_date
        self.first_name = other.get("first_name") if other.get("first_name") else self.first_name
        self.last_name = other.get("last_name") if other.get("last_name") else self.last_name
        try:
            self.save()
        except IntegrityError:
            raise UserAlreadyExists()
        return self

    def get_verification_token(self):
        exp_day, exp_hour, exp_min, exp_sec = VERIFICATION_TOKEN_EXPIRATION_TIME
        if get_current_time() > self.verification_token_time + timedelta(days=exp_day,
                                                                         hours=exp_hour,
                                                                         minutes=exp_min,
                                                                         seconds=exp_sec):
            self.verification_token = uuid.uuid4()
            self.verification_token_time = get_current_time()
            self.save()
        return self.verification_token

    def re_update_verification_token(self):
        self.verification_token = uuid.uuid4()
        self.verification_token_time = get_current_time()
        self.save()
        return self.verification_token

    def generate_ot_token(self):
        self.ot_token = generate_int_token()
        self.ot_token_date = get_current_time()
        try:
            self.save()
        except IntegrityError:
            self.generate_ot_token()
        return self.ot_token

    def get_ot_token(self):
        exp_day, exp_hour, exp_min, exp_sec = OT_TOKEN_EXPIRATION_TIME
        if get_current_time() > self.ot_token_date + timedelta(days=exp_day,
                                                               hours=exp_hour,
                                                               minutes=exp_min,
                                                               seconds=exp_sec):
            self.generate_ot_token()
        return self.ot_token

