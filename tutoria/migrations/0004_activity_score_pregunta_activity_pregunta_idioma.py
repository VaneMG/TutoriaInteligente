from django.db import migrations, models  # Agrega esta línea para importar 'django'

class Migration(migrations.Migration):

    dependencies = [
        ('tutoria', '0003_evaluacion_pregunta_opcionrespuesta_respuestausuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='score',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='pregunta',
            name='activity',
            field=models.ForeignKey(default=None, null=True, on_delete=models.CASCADE, to='tutoria.activity'),
        ),
        migrations.AddField(
            model_name='pregunta',
            name='idioma',
            field=models.CharField(default='n', max_length=50),
        ),
    ]
