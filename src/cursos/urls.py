from django.urls import path
from . import views

app_name = "Cursos"
urlpatterns = [
    path('menu/', views.menu, name='menu'),
    path('curso/', views.course, name='curso'),
]

