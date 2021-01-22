from django.contrib import admin
from user_crud.models import Address, CustomUser, Category
from django.contrib.auth.admin import UserAdmin

@admin.register(CustomUser)
class CustomUser(UserAdmin):
    list_display = ['email', 'is_active', "is_verified", "phone_number"]
    # exclude = ('last_login', 'is_superuser', 'groups', 'user_permissions', 'is_staff', 'date_joined')
    fieldsets = (
        (None, {'fields': (
            'first_name',
            'last_name',
            'email',
            'password',
            'ot_token',
            'ot_token_date',
            'verification_token',
            'verification_token_time',
            'reset_password_attempts',
            'categories',
            'stripe_id',
            'address',
            'gender',
            'name',
            'birth_date',

        )}),
        ('Permissions',
         {'fields': (
             'is_active',
             'is_staff',
             'is_superuser',
             'groups',
             'is_termsandconditions_accepted',
             'is_verified',
             'is_company'
         )}),
        ('Important dates and IPs',
         {'fields': (
             'last_login',
             'date_joined',
             'created_date'
         )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'password1', 'password2'),
        }),
    )
    show_change_link = True
    ordering = ('email',)

@admin.register(Category)
class Category(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Address)
class Address(admin.ModelAdmin):
    list_display = ['hash', 'address1', "address2", 'city']

