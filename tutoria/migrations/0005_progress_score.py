# Generated by Django 5.0.3 on 2024-05-03 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutoria', '0004_activity_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='progress',
            name='score',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
