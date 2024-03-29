# Generated by Django 3.1.3 on 2020-11-29 11:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20201129_1240'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='item',
            options={'verbose_name': 'Новости', 'verbose_name_plural': 'Новости'},
        ),
        migrations.AlterModelOptions(
            name='news',
            options={'verbose_name': 'Новости', 'verbose_name_plural': 'Новости'},
        ),
        migrations.RenameField(
            model_name='news',
            old_name='discriptions',
            new_name='description',
        ),
        migrations.AlterField(
            model_name='news',
            name='poster',
            field=models.ImageField(upload_to='News/', verbose_name='Постер'),
        ),
        migrations.AlterField(
            model_name='news',
            name='pub_data',
            field=models.DateField(default=datetime.date.today, verbose_name='Дата старта'),
        ),
    ]
