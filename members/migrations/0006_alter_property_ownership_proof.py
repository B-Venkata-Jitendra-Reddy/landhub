# Generated by Django 5.1.7 on 2025-04-24 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_property'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='ownership_proof',
            field=models.FileField(upload_to='images/'),
        ),
    ]
