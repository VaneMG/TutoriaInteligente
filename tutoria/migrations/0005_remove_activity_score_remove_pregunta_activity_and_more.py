# Generated by Django 5.0.3 on 2024-03-19 00:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutoria', '0004_activity_score_pregunta_activity_pregunta_idioma'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='score',
        ),
        migrations.RemoveField(
            model_name='pregunta',
            name='activity',
        ),
        migrations.AddField(
            model_name='activity',
            name='puntaje_obtenido',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='tutoria.respuestausuario'),
        ),
    ]