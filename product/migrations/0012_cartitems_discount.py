# Generated by Django 4.1.7 on 2023-04-28 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0011_alter_order_delivery_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitems',
            name='discount',
            field=models.IntegerField(default=0),
        ),
    ]