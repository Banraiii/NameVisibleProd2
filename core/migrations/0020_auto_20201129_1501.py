# Generated by Django 3.1.3 on 2020-11-29 12:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20201129_1458'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='item',
            options={'verbose_name': 'Предмет', 'verbose_name_plural': 'Предметы!'},
        ),
    ]