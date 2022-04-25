from django.urls import path
from . import views

app_name = "cursos"
urlpatterns = [

    path('', views.adcourse_list_view, name='adcourse_list'),
    path('curso/crear/', views.adcourse_create_view, name='adcourse_create'),
    path('curso/editar/<int:id>/', views.adcourse_edit_view, name='adcourse_edit'),
    path('curso/<int:id>/miembros/', views.adcourse_members_view, name='adcourse_members'),
    path('curso/<int:id>/agregar-miembros/', views.adcourse_addmember_view, name='adcourse_add_members'),
    path('curso/<int:id>/agregando-miembro/<int:user_id>/', views.adcourse_addingmember_view, name='adcourse_adding_member'),
    path('curso/<int:id>/eliminar/', views.adcourse_delete_view, name='adcourse_delete'),

    path('curso/<int:id>/add-members/', views.adcourse_addmember_view, name='adcourse_addmember'),

    path('menu/', views.menu, name='menu'),
    path('like/<int:id>/', views.like_curso, name='course_like'),
    path('read/<int:id>/', views.read_lecture, name='course_read_lecture'),
    path('watch/<int:id>/', views.watch_video, name='course_watch_video'),
    path('curso/<int:id>/', views.course_detail_view, name='course_detail'),
    path('curso/agregar-modulo/<int:id>/', views.course_create_module_view, name='course_create_module'),
    path('curso/editar-modulo/<int:id>', views.course_edit_module_view, name='course_edit_module'),
    path('curso/agregar-actividad/<int:id>/<int:action>/', views.course_create_item_view, name='course_create_item'),
    path('curso/editar-actividad/<int:id>/<int:action>/', views.course_edit_item_view, name='course_edit_item'),
    path('curso/lectura/<int:id>/', views.course_lecture_view, name='course_lecture'),
    path('curso/actividad/<int:id>/', views.course_activity_view, name='course_activity'),
    path('curso/video/<int:id>/', views.course_video_view, name='course_video'),
]

