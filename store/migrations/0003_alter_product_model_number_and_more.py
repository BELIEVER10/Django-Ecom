# Generated by Django 5.2 on 2025-05-08 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_product_is_left_banner_offer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='model_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='variation',
            name='model_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
