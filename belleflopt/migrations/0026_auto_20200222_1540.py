# Generated by Django 2.2.4 on 2020-02-22 23:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('belleflopt', '0025_auto_20200222_1530'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='streamsegment',
            name='belleflopt__downstr_c30b7c_idx',
        ),
        migrations.AddIndex(
            model_name='dailyflow',
            index=models.Index(fields=['water_year', 'water_year_day'], name='idx_water_yr_and_day'),
        ),
        migrations.AddIndex(
            model_name='dailyflow',
            index=models.Index(fields=['water_year'], name='idx_water_year'),
        ),
        migrations.AddIndex(
            model_name='dailyflow',
            index=models.Index(fields=['water_year_day'], name='idx_water_year_day'),
        ),
    ]
