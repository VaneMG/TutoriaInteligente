from django.contrib import admin
from django.urls import path
from tutoria import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Ruta para la página de inicio
    path('register/', views.register, name='register'),  # Ruta para el registro de nuevos usuarios
    path('change_password/', views.change_password, name='change_password'),  # Ruta para cambiar la contraseña del usuario
    path('accounts/login/', views.login_view, name='login'),  # Ruta para el inicio de sesión personalizado
    # Elimina la inclusión de las URLs de autenticación proporcionadas por Django
    path('logout/', views.logout_view, name='logout'),  # Asegúrate de definir esta URL
    path('about/', views.about, name='about'),  # Ruta para la página "About"
    path('profile/', views.profile, name='profile'),  # Ruta para la página "Profile"
    path('course/<str:course_name>/', views.course_detail, name='course_detail'),  # Ruta para ver detalles del curso por nombre
    path('courses/', views.courses, name='courses'),  # Ruta para la página "Courses"
    path('activities/', views.activities, name='activities'),
    path('activity/<int:activity_id>/', views.activity_detail, name='activity_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
