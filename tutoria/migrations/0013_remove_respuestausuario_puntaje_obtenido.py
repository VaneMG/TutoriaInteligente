# Generated by Django 5.0.3 on 2024-03-21 22:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutoria', '0012_student_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='respuestausuario',
            name='puntaje_obtenido',
        ),
    ]
