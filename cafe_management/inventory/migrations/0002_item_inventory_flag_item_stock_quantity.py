# Generated by Django 5.0.2 on 2024-08-26 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='inventory_flag',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='item',
            name='stock_quantity',
            field=models.IntegerField(default=0),
        ),
    ]
