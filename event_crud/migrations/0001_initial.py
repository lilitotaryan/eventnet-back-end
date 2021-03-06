# Generated by Django 2.2.5 on 2020-02-26 19:01

import authentication.utils
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_crud', '0005_remove_customuser_phone_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default=None, max_length=100)),
                ('description', models.CharField(default=None, max_length=500)),
                ('date', models.DateTimeField(default=authentication.utils.get_current_time)),
                ('is_responsible', models.BooleanField(default=False)),
                ('contact_phone_number', models.CharField(default=None, max_length=100, unique=True)),
                ('address', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_crud.Address')),
                ('categories', models.ManyToManyField(blank=True, to='user_crud.Category')),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
