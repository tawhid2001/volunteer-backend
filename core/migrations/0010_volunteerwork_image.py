# Generated by Django 4.2 on 2024-09-02 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_profile_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteerwork',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='work_images/'),
        ),
    ]
