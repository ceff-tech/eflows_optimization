# Generated by Django 2.2.4 on 2019-09-19 23:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('belleflopt', '0012_auto_20190919_1631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='segmentcomponent',
            name='maximum_magnitude',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='segmentcomponent',
            name='minimum_magnitude',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True),
        ),
    ]
