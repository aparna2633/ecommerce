# Generated by Django 4.1.7 on 2023-04-29 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_cartitems_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='coupon_code',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]
