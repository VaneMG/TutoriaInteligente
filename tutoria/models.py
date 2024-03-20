from django.db import models


class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    age = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='course_images', default='default.jpg')

    def __str__(self):
        return self.title

class Activity(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Campo para almacenar el puntaje

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
    puntaje_obtenido = models.IntegerField(default=0)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, default=None, null=True)

    def __str__(self):
        return f"Respuesta de {self.pregunta.texto}"

class Progress(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} - {self.activity.name}"
