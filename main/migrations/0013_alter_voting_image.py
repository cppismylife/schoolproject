# Generated by Django 3.2.5 on 2021-07-28 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20210728_1716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voting',
            name='image',
            field=models.ImageField(blank=True, upload_to='votings'),
        ),
    ]
