from django.contrib import admin
from .models import Student, Course, Activity, Progress, Pregunta, OpcionRespuesta, RespuestaUsuario, Notification

admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Activity)
admin.site.register(Progress)
admin.site.register(Pregunta)
admin.site.register(OpcionRespuesta)
admin.site.register(RespuestaUsuario)
admin.site.register(Notification)
