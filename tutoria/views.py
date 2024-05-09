from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import F
from .models import User, Course, Activity, Student, Progress, OpcionRespuesta, RespuestaUsuario, Pregunta, Notification
from .recommendation_logic import recommend_activities
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db import transaction
import uuid
from django.utils import timezone
from django.db import IntegrityError 
from django.core.paginator import Paginator, EmptyPage
from collections.abc import Iterable, Iterator
from django.contrib.auth.forms import PasswordChangeForm 


def home(request):
    return render(request, 'home.html')

def courses(request):
    courses = Course.objects.all()
    return render(request, 'courses.html', {'courses': courses})

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
            return redirect('login')
        else:
            messages.error(request, '¡El usuario ya existe! Por favor, elige otro nombre de usuario.')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def change_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        # Verificar si el nombre de usuario y la contraseña coinciden
        user = User.objects.filter(username=username).first()
        if not user or not user.check_password(old_password):
            messages.error(request, 'El nombre de usuario y la contraseña no coinciden.')
            return redirect('change_password')

        # Crear el formulario para cambiar la contraseña
        form = PasswordChangeForm(user, request.POST)
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

# IMPLEMENTA PATRON OBSERVER PARA NOTIFICACIONES
def profile(request):
    # Obtener el usuario que ha iniciado sesión
    user = request.user

    try:
        # Buscar el estudiante asociado a ese usuario
        student = Student.objects.get(user=user)
        
        # Obtener el progreso del estudiante (actividades completadas)
        progress = Progress.objects.filter(student=student, completed=True)

        # Obtener las notificaciones para este estudiante
        notifications = Notification.objects.filter(student=student).order_by('-timestamp')
        
        # Crear una lista para almacenar información de cada actividad completada
        completed_activities = []
        for progress_item in progress:
            activity = progress_item.activity
            # Obtener la calificación final de la actividad desde el progreso
            score = progress_item.score
            completed_activities.append({'activity': activity, 'score': score})

        # Obtener las áreas de mejora del estudiante
        student_activities = student.areas_mejora.split(", ")[:-1]

        # Pasar los datos al template 'profile.html', incluyendo student_activities
        return render(request, 'profile.html', {'student': student, 'completed_activities': completed_activities, 'notifications': notifications, 'student_activities': student_activities})
    
    except Student.DoesNotExist:
        # Si no se encuentra información del estudiante asociada al usuario, mostrar un mensaje de error
        messages.error(request, 'No se encontró información de estudiante asociada a este usuario.')
        return redirect('home')

    
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
        # Obtener las actividades recomendadas excluyendo aquellas completadas con una calificación alta (mayor a 80)
        recommended_activities = recommend_activities(student).exclude(score__gt=80)

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

# IMPLEMENTACIÓN DEL PATRON DE ITERADOR PARA MOSTRAR LAS PREGUNTAS
class PreguntaIterator(Iterator):
    def __init__(self, preguntas):
        self._preguntas = preguntas
        self._index = 0

    def __next__(self):
        if self._index < len(self._preguntas):
            pregunta = self._preguntas[self._index]
            self._index += 1
            return pregunta
        raise StopIteration

@login_required
def activity_detail(request, activity_id):
    # Obtener el estudiante asociado al usuario que inició sesión
    student = request.user.student
    
    # Obtener la actividad
    activity = get_object_or_404(Activity, pk=activity_id)
    
    # Obtener todas las preguntas asociadas con la actividad
    preguntas = Pregunta.objects.filter(activity=activity).prefetch_related('opcionrespuesta_set')

    # Crear el iterador de preguntas
    pregunta_iterator = PreguntaIterator(preguntas)

    # Inicializar total_score como cero en caso de no ser una solicitud POST
    total_score = 0

    if request.method == 'POST':
        # Obtener el estudiante asociado al usuario que inició sesión
        student = request.user.student
        
        # Guardar las respuestas del usuario en la base de datos y calcular el puntaje total
        for pregunta in pregunta_iterator:
            question_id = f'question_{pregunta.id}'
            selected_answer_id = request.POST.get(question_id)
            if selected_answer_id is not None:
                selected_answer = OpcionRespuesta.objects.get(pk=selected_answer_id)
                # Verificar si la opción seleccionada es correcta
                if selected_answer.es_correcta:
                    total_score += 1
                # Guardar la respuesta del usuario en la tabla RespuestaUsuario
                respuesta_usuario = RespuestaUsuario.objects.create(pregunta=pregunta, opcion_elegida=selected_answer, estudiante=student)

        # Calcular la calificación final y actualizar el atributo score en la tabla Activity
        final_score = (total_score / preguntas.count()) * 100
        activity.score = final_score
        activity.save()

        # Si el puntaje es menor o igual a 50, agregar el nombre de la actividad a areas_mejora del estudiante
        if final_score <= 50:
            if student.areas_mejora is None:
                student.areas_mejora = ''
                # Convertir las actividades de mejora existentes en un conjunto
                existing_activities = set(student.areas_mejora.split(", ") if student.areas_mejora else [])
                # Agregar la nueva actividad al conjunto
                existing_activities.add(activity.name)
                # Convertir el conjunto nuevamente en una cadena separada por comas y actualizar el campo
                student.areas_mejora = ', '.join(existing_activities)
                student.save()

            # Crear una notificación para esta actividad completada con calificación baja
            with transaction.atomic():
                notification_message = f"Has completado la actividad '{activity.name}' con una calificación baja."
                try:
                    new_notification = Notification.objects.create(student=student, message=notification_message, timestamp=timezone.now())
                    print("Nueva notificación creada:", new_notification)    
                except IntegrityError as e:
                    print("Error al crear la notificación:", e)

        # Actualizar el progreso del estudiante
        with transaction.atomic():
            progress, created = Progress.objects.get_or_create(student=student, activity=activity)
            progress.completed = True
            progress.score = final_score  # Actualizar el puntaje en el progreso
            progress.save()

            # Si el ID de la actividad es 1, calcular el nivel de idioma basado en la calificación final
            if activity.id == 1:
                if final_score <= 60:
                    student.nivel_idioma = 'basico'
                elif final_score <= 80:
                    student.nivel_idioma = 'intermedio'
                else:
                    student.nivel_idioma = 'avanzado'
                student.save()

                # Crear una notificación para esta actividad completada
                notification_message = f"Has completado la actividad '{activity.name}'"
                try:
                    new_notification = Notification.objects.create(student=student, message=notification_message, timestamp=timezone.now())
                    print("Nueva notificación creada:", new_notification)    
                except IntegrityError as e:
                    print("Error al crear la notificación:", e)

        # Devolver el resultado como JSON
        return JsonResponse({'total_score': total_score, 'final_score': activity.score})

    # Verificar si hay actividades de mejora antes de pasarlas al contexto de renderizado
    if student.areas_mejora:
        # Dividir las actividades de mejora en una lista y eliminar el último elemento (que sería una cadena vacía)
        student_activities = student.areas_mejora.split(", ")[:-1]
    else:
        # Si no hay actividades de mejora, establecer la lista como vacía
        student_activities = []

    # Pasar la lista de actividades de mejora al contexto de renderizado
    return render(request, 'activity_detail.html', {'activity': activity, 'preguntas': pregunta_iterator, 'total_score': total_score, 'student_activities': student_activities})


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