# Generated by Django 4.0.4 on 2022-05-06 00:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_alter_comment_auction_alter_listing_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='watchlist',
            old_name='item',
            new_name='listing',
        ),
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(blank=True, choices=[('Home', 'Home'), ('Toys', 'Toys'), ('Electronics', 'Electronics'), ('Other', 'Other'), ('Fashion', 'Fashion')], max_length=64, null=True),
        ),
    ]
