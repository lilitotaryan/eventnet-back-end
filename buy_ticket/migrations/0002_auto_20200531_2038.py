# Generated by Django 2.2.5 on 2020-05-31 20:38

import authentication.utils
import buy_ticket.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buy_ticket', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.IntegerField(default=buy_ticket.utils.id_generator, unique=True)),
                ('start_time', models.DateTimeField(default=authentication.utils.get_current_time)),
                ('end_time', models.DateTimeField(default=authentication.utils.get_current_time)),
                ('amount', models.IntegerField(default=0)),
                ('quantity', models.IntegerField(default=1)),
                ('is_vip', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='ticket',
            name='additional_info',
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]
