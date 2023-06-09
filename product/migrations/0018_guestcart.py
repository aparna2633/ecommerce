# Generated by Django 4.1.7 on 2023-05-05 18:15

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0017_rename_image1_banner_image_rename_tag_banner_title_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GuestCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_ref', models.CharField(max_length=200)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=50, null=True)),
                ('quantity', models.IntegerField(default=1)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=50, null=True)),
                ('created_at', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product')),
            ],
        ),
    ]
