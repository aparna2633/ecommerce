# Generated by Django 4.1.7 on 2023-05-03 15:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0016_banner'),
    ]

    operations = [
        migrations.RenameField(
            model_name='banner',
            old_name='image1',
            new_name='image',
        ),
        migrations.RenameField(
            model_name='banner',
            old_name='tag',
            new_name='title',
        ),
        migrations.RemoveField(
            model_name='banner',
            name='title1',
        ),
        migrations.RemoveField(
            model_name='banner',
            name='title2',
        ),
    ]
