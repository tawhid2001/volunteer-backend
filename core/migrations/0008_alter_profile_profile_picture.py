# Generated by Django 4.2 on 2024-09-02 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_profile_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_picture',
            field=models.ImageField(default='./core/media/image/default_profile.jpg', upload_to='./core/media/profile_pics/'),
        ),
    ]
