from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    NIVEL_IDIOMA_CHOICES = [
        ('basico', 'Básico'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    areas_mejora = models.TextField(null=True, blank=True, default=None)  # Agregar campo de áreas de mejora
    nivel_idioma = models.CharField(max_length=20, choices=NIVEL_IDIOMA_CHOICES, null=True, blank=True, default=None)

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='course_images', default='default.jpg')

    def __str__(self):
        return self.title

class Activity(models.Model):
    EVALUACION = 'evaluacion'
    BASIC = 'basico'
    INTERMEDIATE = 'intermedio'
    ADVANCED = 'avanzado'
    LEVEL_CHOICES = [
        (BASIC, 'Básico'),
        (INTERMEDIATE, 'Intermedio'),
        (ADVANCED, 'Avanzado'),
        (EVALUACION, 'Evaluación'),  
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    nivel = models.CharField(max_length=20, choices=LEVEL_CHOICES, null=True, default=None)
    score = models.FloatField(null=True, blank=True)  
    

    def __str__(self):
        return self.name

        
class Pregunta(models.Model):
    texto = models.TextField()
    idioma = models.CharField(max_length=50, default='n')  
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, default=None, null=True)

    def __str__(self):
        return self.texto

class OpcionRespuesta(models.Model):
    texto = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)

    def __str__(self):
        return self.texto

class RespuestaUsuario(models.Model):
    pregunta = models.ForeignKey('Pregunta', on_delete=models.CASCADE)
    opcion_elegida = models.ForeignKey('OpcionRespuesta', on_delete=models.CASCADE)
    estudiante = models.ForeignKey(Student, on_delete=models.CASCADE, default=None)  # Relación con la tabla Student para heredar el nombre del estudiante
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Campo para almacenar el puntaje

    def __str__(self):
        return f"Respuesta de {self.pregunta.texto} por {self.estudiante.name if self.estudiante else 'Anónimo'}"
    
class Progress(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.name} - {self.activity.name}"
    
class Notification(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

class Recomendacion(models.Model):
    activity = models.ForeignKey('Activity', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    urls_material = models.TextField(help_text="Ingresa los URLs del material, separados por comas.")

    def obtener_lista_urls(self):
        return self.urls_material.split(',')

    def __str__(self):
        return f"{self.titulo} - {self.activity.name}"