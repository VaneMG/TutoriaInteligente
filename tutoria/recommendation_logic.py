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
        print("Actividades recomendadas para nivel básico:", recommended_activities)

    # Regla 2: Recomendar actividades intermedias si el nivel de idioma es intermedio
    elif language_level == 'intermedio':
        recommended_activities.extend(Activity.objects.filter(nivel='intermedio'))
        print("Actividades recomendadas para nivel intermedio:", recommended_activities)

    # Regla 3: Recomendar actividades avanzadas si el nivel de idioma es avanzado
    elif language_level == 'avanzado':
        recommended_activities.extend(Activity.objects.filter(nivel='avanzado'))
        print("Actividades recomendadas para nivel avanzado:", recommended_activities)

    # Regla 4: Recomendar actividades basadas en el progreso del estudiante
    for progress in user_progress:
            # Filtrar por nivel de idioma
            if progress.activity.nivel == language_level:
                # Agregar la actividad si no está en la lista de recomendadas
                if progress.activity not in recommended_activities:
                    recommended_activities.append(progress.activity)

    # Impresión de registro para verificar las actividades recomendadas finales
    print("Actividades recomendadas finales:", recommended_activities)

    return recommended_activities
