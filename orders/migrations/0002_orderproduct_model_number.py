# Generated by Django 5.2 on 2025-05-08 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproduct',
            name='model_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
