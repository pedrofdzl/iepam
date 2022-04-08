from django.urls import path
from . import views

app_name = "cursos"
urlpatterns = [

    path('', views.adcourse_list_view, name='adcourse_list'),
    path('curso/crear/', views.adcourse_create_view, name='adcourse_create'),
    path('curso/<int:id>/', views.adcourse_detail_view, name='adcourse_detail'),
    path('curso/<int:id>/miembros/', views.adcourse_members_view, name='adcourse_members'),
    path('curso/<int:id>/agregar-miembros/', views.adcourse_addmember_view, name='adcourse_add_members'),
    path('curso/<int:id>/agregando-miembro/<int:user_id>/', views.adcourse_addingmember_view, name='adcourse_adding_member'),
    path('curso/<int:id>/eliminar/', views.adcourse_delete_view, name='adcourse_delete'),

    path('curso/<int:id>/add-members/', views.adcourse_addmember_view, name='adcourse_addmember'),

    path('menu/', views.menu, name='menu'),
    path('curso/', views.course, name='curso'),
]

