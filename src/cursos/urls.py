from django.urls import path
from . import views

app_name = "Cursos"
urlpatterns = [
    path('capacitacion/', views.course, name='course'),
]

