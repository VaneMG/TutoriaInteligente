# Generated by Django 5.0.3 on 2024-04-02 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutoria', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='nivel',
            field=models.CharField(choices=[('basico', 'Básico'), ('intermedio', 'Intermedio'), ('avanzado', 'Avanzado'), ('evaluacion', 'Evaluación')], default=None, max_length=20, null=True),
        ),
    ]
