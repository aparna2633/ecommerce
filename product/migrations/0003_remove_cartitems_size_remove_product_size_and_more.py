# Generated by Django 4.1.4 on 2023-01-14 07:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_cartitems_size_product_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitems',
            name='size',
        ),
        migrations.RemoveField(
            model_name='product',
            name='size',
        ),
        migrations.DeleteModel(
            name='Size',
        ),
    ]
