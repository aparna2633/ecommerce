# Generated by Django 4.1.7 on 2023-05-06 13:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0018_guestcart'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='discount_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]