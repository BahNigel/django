# Generated by Django 4.2.1 on 2023-06-05 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_blog'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='user_id',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
