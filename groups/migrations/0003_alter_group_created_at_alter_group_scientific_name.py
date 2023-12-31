# Generated by Django 4.2.6 on 2023-10-05 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_group_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='scientific_name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
