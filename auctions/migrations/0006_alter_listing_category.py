# Generated by Django 4.0.4 on 2022-05-22 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_listing_closed_alter_listing_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(blank=True, choices=[('Home', 'Home'), ('Other', 'Other'), ('Electronics', 'Electronics'), ('Fashion', 'Fashion'), ('Toys', 'Toys')], max_length=64, null=True),
        ),
    ]