# Generated by Django 4.2 on 2023-04-29 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='sunbak_Crawl_DataModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imgsrc', models.URLField()),
                ('title', models.CharField(max_length=100)),
                ('price', models.CharField(max_length=15)),
                ('boardType', models.CharField(max_length=10)),
            ],
        ),
    ]