# Generated by Django 5.0.3 on 2024-03-21 02:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutoria', '0009_remove_respuestausuario_activity'),
    ]

    operations = [
        migrations.AddField(
            model_name='respuestausuario',
            name='estudiante',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='tutoria.student'),
        ),
    ]