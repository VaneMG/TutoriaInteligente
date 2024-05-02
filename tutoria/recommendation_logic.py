from .models import Activity, Progress

# Función para recomendar actividades al estudiante
def recommend_activities(student):
    # Obtener el progreso del estudiante
    user_progress = Progress.objects.filter(student=student)

    # Calcular el nivel de idioma del estudiante
    language_level = student.nivel_idioma

    # Definir reglas heurísticas para hacer recomendaciones
    recommended_activities = []

    # Regla 1: Recomendar actividades básicas si el nivel de idioma es básico
    if language_level == 'basico':
        recommended_activities.extend(Activity.objects.filter(nivel='basico'))

    # Regla 2: Recomendar actividades intermedias si el nivel de idioma es intermedio
    elif language_level == 'intermedio':
        recommended_activities.extend(Activity.objects.filter(nivel='intermedio'))

    # Regla 3: Recomendar actividades avanzadas si el nivel de idioma es avanzado
    elif language_level == 'avanzado':
        recommended_activities.extend(Activity.objects.filter(nivel='avanzado'))

    # Regla 4: Recomendar actividades basadas en el progreso del estudiante
    for progress in user_progress:
        # Filtrar por nivel de idioma
        if progress.activity.nivel == language_level:
            # Agregar la actividad si no está en la lista de recomendadas y no está completada
            if progress.activity not in recommended_activities and not progress.completed:
                recommended_activities.append(progress.activity)

    return recommended_activities
