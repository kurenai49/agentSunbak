# Generated by Django 4.2 on 2023-08-01 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sunbak_crawler', '0016_sunbak_crawl_datamodel_tons'),
    ]

    operations = [
        migrations.AddField(
            model_name='sunbak_crawl_datamodel',
            name='modelYear',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
    ]
