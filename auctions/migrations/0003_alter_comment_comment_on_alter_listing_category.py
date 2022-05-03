# Generated by Django 4.0.4 on 2022-05-03 01:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_alter_listing_category_alter_listing_img_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='comment_on',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='auctions.listing'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(blank=True, choices=[('Home', 'Home'), ('Electronics', 'Electronics'), ('Fashion', 'Fashion'), ('Toys', 'Toys')], max_length=64, null=True),
        ),
    ]
