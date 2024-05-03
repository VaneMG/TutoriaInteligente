from .models import Activity, Progress
from django.db.models import Q

def recommend_activities(student):
    # Obtener el progreso del estudiante
    user_progress = Progress.objects.filter(student=student)
    
    # Obtener el nivel de idioma del estudiante
    language_level = student.nivel_idioma
    
    # Definir reglas heurísticas para hacer recomendaciones
    recommended_activities = Activity.objects.none()

    # Filtrar actividades basadas en el nivel de idioma del estudiante
    if language_level == 'basico':
        recommended_activities = Activity.objects.filter(nivel='basico')
    elif language_level == 'intermedio':
        recommended_activities = Activity.objects.filter(nivel='intermedio')
    elif language_level == 'avanzado':
        recommended_activities = Activity.objects.filter(nivel='avanzado')

    # Excluir las actividades completadas con una calificación alta
    for progress in user_progress:
        if progress.activity in recommended_activities:
            if progress.score is not None and progress.score > 80:
                recommended_activities = recommended_activities.exclude(id=progress.activity.id)

    return recommended_activities