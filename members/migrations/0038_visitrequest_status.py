# Generated by Django 5.1.7 on 2025-06-15 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0037_userprofile_is_agent_application_pending_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitrequest',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=20),
        ),
    ]
