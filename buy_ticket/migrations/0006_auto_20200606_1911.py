# Generated by Django 2.2.5 on 2020-06-06 19:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event_crud', '0018_auto_20200606_1911'),
        ('buy_ticket', '0005_payment_is_expired'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='event_crud.Event'),
        ),
        migrations.AddField(
            model_name='payment',
            name='refund_id',
            field=models.CharField(max_length=100, null=True),
        ),
    ]