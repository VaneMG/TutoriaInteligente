from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import F
from .models import Course, Activity, Student, Progress, OpcionRespuesta, RespuestaUsuario, Pregunta
from django.http import JsonResponse
from django.template.loader import render_to_string


def home(request):
    return render(request, 'home.html')

def course_detail(request, course_name):
    course = get_object_or_404(Course, title=course_name)
    return render(request, 'course_detail.html', {'course': course})

def student_detail(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    progress = Progress.objects.filter(student=student)
    return render(request, 'student_detail.html', {'student': student, 'progress': progress})

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
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            auth_login(request, user)
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
    user = request.user
    try:
        student = Student.objects.get(user=user)
        progress = Progress.objects.filter(student=student)
        return render(request, 'profile.html', {'student': student, 'progress': progress})
    except Student.DoesNotExist:
        messages.error(request, 'No se encontró información de estudiante asociada a este usuario.')
        return redirect('home')

def courses(request):
    courses = Course.objects.all()
    return render(request, 'courses.html', {'courses': courses})

def activities(request):
    activities = Activity.objects.all()  # Obtener todas las actividades desde la base de datos
    return render(request, 'activities.html', {'activities': activities})

def activity_detail(request, activity_id):
    # Obtener la actividad
    activity = get_object_or_404(Activity, pk=activity_id)
    
    # Obtener todas las preguntas asociadas con la actividad
    preguntas = Pregunta.objects.filter(activity=activity).prefetch_related('opcionrespuesta_set')

    # Inicializar total_score como cero en caso de no ser una solicitud POST
    total_score = 0

    if request.method == 'POST':
        # Inicializar variables para el puntaje total y el número total de preguntas
        total_questions = 0

        # Guardar las respuestas del usuario en la base de datos y calcular el puntaje total
        for pregunta in preguntas:
            question_id = f'question_{pregunta.id}'
            selected_answer_id = request.POST.get(question_id)
            if selected_answer_id is not None:
                total_questions += 1
                selected_answer = OpcionRespuesta.objects.get(pk=selected_answer_id)
                if selected_answer.es_correcta:
                    total_score += 1

        # Devolver el puntaje total como una respuesta JSON
        score_html = f'<p>Puntaje total: {total_score} correctas de {preguntas.count()} preguntas</p>'
        return JsonResponse({'score_html': score_html})

    # Renderizar la página de detalles de la actividad con el formulario
    return render(request, 'activity_detail.html', {'activity': activity, 'preguntas': preguntas, 'total_score': total_score})