# Generated by Django 4.1.7 on 2023-05-01 06:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_alter_coupon_coupon_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='address',
            new_name='address1',
        ),
    ]