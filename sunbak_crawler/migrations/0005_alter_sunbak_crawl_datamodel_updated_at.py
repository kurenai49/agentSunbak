# Generated by Django 4.2 on 2023-05-01 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sunbak_crawler', '0004_sunbak_crawl_datamodel_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sunbak_crawl_datamodel',
            name='updated_at',
            field=models.DateField(null=True),
        ),
    ]