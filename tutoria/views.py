from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import F
from .models import Course, Activity, Student, Progress, OpcionRespuesta, RespuestaUsuario, Pregunta
from .recommendation_logic import recommend_activities
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db import transaction
import uuid


def home(request):
    return render(request, 'home.html')

def course_detail(request, course_name):
    course = get_object_or_404(Course, title=course_name)
    return render(request, 'course_detail.html', {'course': course})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            student = Student.objects.create(user=user, name=user.username)
            messages.success(request, '¡Registro exitoso! Ahora puedes iniciar sesión.')
            return redirect('home')
        else:
            messages.error(request, '¡El usuario ya existe! Por favor, elige otro nombre de usuario.')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            messages.success(request, 'Contraseña cambiada correctamente.')
            return redirect('login')
        else:
            messages.error(request, 'Por favor, corrija los errores a continuación.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('login')

def about(request):
    return render(request, 'about.html')

def profile(request):
    # Obtener el usuario que ha iniciado sesión
    user = request.user

    try:
        # Buscar el estudiante asociado a ese usuario
        student = Student.objects.get(user=user)
        
        # Obtener el progreso del estudiante (actividades completadas)
        progress = Progress.objects.filter(student=student, completed=True)

        # Pasar los datos al template 'profile.html'
        return render(request, 'profile.html', {'student': student, 'progress': progress})
    
    except Student.DoesNotExist:
        # Si no se encuentra información del estudiante asociada al usuario, mostrar un mensaje de error
        messages.error(request, 'No se encontró información de estudiante asociada a este usuario.')
        return redirect('home')

def courses(request):
    courses = Course.objects.all()
    return render(request, 'courses.html', {'courses': courses})

from django.db.models import Count

@login_required
def activities(request):
    # Obtener el estudiante asociado al usuario que ha iniciado sesión
    student = request.user.student

    # Obtener todas las actividades completadas por el estudiante
    completed_activities = Progress.objects.filter(student=student, completed=True)

    # Obtener la evaluación de idioma del estudiante si está disponible
    language_assessment = Activity.objects.filter(name='Evaluación - Nivel Aprendizaje').first()

    # Verificar si el examen de evaluación de idioma está completado
    has_language_assessment_completed = False
    if language_assessment:
        has_language_assessment_completed = language_assessment.id in [activity.activity.id for activity in completed_activities]

    # Obtener las actividades recomendadas que aún no han sido completadas
    recommended_activities = []
    if has_language_assessment_completed:
        recommended_activities = recommend_activities(student)  # Llamar a la función recommend_activities para obtener las actividades recomendadas

    # Imprimir el contenido del contexto para verificar las actividades recomendadas
    print("Contenido del contexto:", recommended_activities)

    # Pasar las variables de contexto a la plantilla
    context = {
        'recommended_activities': recommended_activities,
        'has_language_assessment_completed': has_language_assessment_completed,
        'language_assessment': language_assessment  # Pasar la actividad de evaluación de idioma al contexto
    }

    # Renderizar la plantilla con las variables de contexto
    return render(request, 'activities.html', context)



@login_required
def activity_detail(request, activity_id):
    # Obtener la actividad
    activity = get_object_or_404(Activity, pk=activity_id)
    
    # Obtener todas las preguntas asociadas con la actividad
    preguntas = Pregunta.objects.filter(activity=activity).prefetch_related('opcionrespuesta_set')

    # Inicializar total_score como cero en caso de no ser una solicitud POST
    total_score = 0

    if request.method == 'POST':
        # Obtener el estudiante asociado al usuario que inició sesión
        student = request.user.student
        
        # Guardar las respuestas del usuario en la base de datos y calcular el puntaje total
        for pregunta in preguntas:
            question_id = f'question_{pregunta.id}'
            selected_answer_id = request.POST.get(question_id)
            if selected_answer_id is not None:
                total_score += 1
                selected_answer = OpcionRespuesta.objects.get(pk=selected_answer_id)
                # Guardar la respuesta del usuario en la tabla RespuestaUsuario
                respuesta_usuario = RespuestaUsuario.objects.create(pregunta=pregunta, opcion_elegida=selected_answer, estudiante=student)
                # Calcular la calificación de la pregunta y guardarla en el campo score de RespuestaUsuario
                respuesta_usuario.score = 100 / preguntas.count()  # Asignar 100 puntos divididos por el número de preguntas como puntaje por pregunta
                respuesta_usuario.save()

        # Calcular la calificación final y actualizar el atributo score en la tabla Activity
        final_score = (total_score / preguntas.count()) * 100
        activity.score = final_score
        activity.save()

        # Si el ID de la actividad es 1, calcular el nivel de idioma basado en la calificación final
        if activity.id == 1:
            student = request.user.student
            if final_score <= 60:
                student.nivel_idioma = 'basico'
            elif final_score <= 80:
                student.nivel_idioma = 'intermedio'
            else:
                student.nivel_idioma = 'avanzado'
            student.save()

            # Actualizar el progreso del estudiante
            with transaction.atomic():
                progress, created = Progress.objects.get_or_create(student=student, activity=activity)
                progress.completed = True
                progress.save()

        # Si la actividad es diferente de 1 y el puntaje es igual o menor a 50, agregar el nombre de la actividad a areas_mejora
        elif final_score <= 50:
            student = request.user.student
            student.areas_mejora = student.areas_mejora + f'{activity.title}, '
            student.save()

        # Devolver el resultado como JSON
        return JsonResponse({'total_score': total_score, 'final_score': activity.score})

    # Si no es una solicitud POST o si aún no se ha enviado el formulario, renderizar la plantilla con los datos de la actividad y las preguntas
    return render(request, 'activity_detail.html', {'activity': activity, 'preguntas': preguntas, 'total_score': total_score})
# IMPLEMENTACIÓN DEL PATRON SINGLETON

class SessionManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SessionManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.sessions = {}

    def create_session(self, user_id):
        session_id = str(uuid.uuid4())  # Genera un UUID único
        self.sessions[session_id] = user_id
        return session_id

    def get_user_id(self, session_id):
        return self.sessions.get(session_id)