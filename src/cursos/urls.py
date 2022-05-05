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
    path('curso/<int:id>/remover-miembro/<int:user_id>/', views.adcourse_members_remove_view, name='adcourse_removing_member'),
    path('curso/<int:id>/eliminar/', views.course_delete_view, name='adcourse_delete'),

    path('curso/<int:id>/add-members/', views.adcourse_addmember_view, name='adcourse_addmember'),
    path('curso/<int:id>/salir/', views.course_leave_view, name='course_quit'),


    path('menu/', views.menu, name='menu'),
    path('like/<int:id>/', views.like_curso, name='course_like'),
    path('read/<int:id>/', views.read_lecture, name='course_read_lecture'),
    path('watch/<int:id>/', views.watch_video, name='course_watch_video'),
    path('curso/<int:id>/', views.course_detail_view, name='course_detail'),

    # Modulos
    path('curso/agregar-modulo/<int:id>/', views.course_create_module_view, name='course_create_module'),
    path('curso/editar-modulo/<int:id>/', views.course_edit_module_view, name='course_edit_module'),


    path('curso/agregar-actividad/<int:id>/<int:action>/', views.course_create_item_view, name='course_create_item'),
    path('curso/editar-actividad/<int:id>/<int:action>/', views.course_edit_item_view, name='course_edit_item'),


    # Lecturas
    path('curso/lectura/<int:id>/', views.course_lecture_view, name='course_lecture'),
    path("curso/lectura/<int:id>/eliminar/", views.course_lecture_delete_view, name='course_lecture_delete'),


    # Actividades
    path('curso/actividad/<int:id>/', views.course_activity_view, name='course_activity'),
    path('curso/actividad/<int:id>/eliminar', views.course_activity_delete_view, name='course_activity_delete'),
    path('curso/entrega/<int:id>/', views.course_activity_entry_detail_view, name='course_activity_entry'),
    path('curso/entrega/<int:id>/archivo/', views.course_activity_entry_file_view, name='course_activity_entry_file'),
    path('curso/entrega/<int:id>/eliminar/', views.course_activity_entry_delete_view, name='course_activity_entry_delete'),


    # Videos
    path('curso/video/<int:id>/', views.course_video_view, name='course_video'),
    path('curso/video/<int:id>/eliminar/', views.course_video_delete_view, name='course_video_delete'),


    # Cursos
    path('curso/recurso/<int:id>/', views.course_resource_view, name='course_resource'),
    path('curso/recurso/<int:id>/eliminar/', views.course_resource_delete_view, name='course_resource_delete'),
    path('curso/recurso/<int:id>/archivo/', views.course_resource_download_view, name='course_resource_file'),
    

    # Hangman
    path('curso/hangman/<int:id>/', views.course_hangman_view, name='course_hangman'),
    path('curso/hangman/<int:id>/eliminar/', views.course_hangman_delete_view, name='course_hangman_delete'),
    path('curso/hangman/<int:id>/crear-opcion/', views.course_hangman_option_create_view, name='course_hangman_add_option'),
    path('curso/hangman/<int:id>/editar-opcion/', views.course_hangman_option_edit_view, name='course_hangman_edit_option'),
    path('curso/hangman/<int:id>/eliminar-opcion/', views.course_hangman_option_delete_view, name='course_hangman_delete_option'),


    # Quiz
    path('curso/quiz/<int:id>/', views.course_quiz_view, name='course_quiz'),
    path('curso/quiz/<int:id>/eliminar/', views.course_quiz_delete_view, name='course_quiz_delete'),
    path('curso/quiz/<int:id>/answer/', views.course_quiz_answer_view, name='course_quiz_answer'),
    path('curso/quiz/<int:id>/answered/', views.course_quiz_answered_view, name='course_quiz_answered'),
    path('curso/quiz/<int:id>/submit/<int:calif>/', views.course_quiz_submit_view, name='course_quiz_submit'),
    path('curso/quiz/<int:id>/agregar-pregunta/', views.course_quiz_create_question_view, name='course_quiz_add_question'),
    path('curso/quiz/<int:id>/editar-pregunta/', views.course_quiz_update_question_view, name='course_quiz_edit_question'),
    path('curso/quiz/<int:id>/eliminar-pregunta/', views.course_quiz_delete_question_view, name='course_quiz_delete_question'),
    path('curso/quiz/<int:id>/agregar-opcion/', views.course_quiz_option_create_view, name='curso_question_add_option'),
    path('curso/quiz/<int:id>/editar-opcion/', views.course_quiz_option_update_view, name='curso_question_edit_option'),
    path('curso/quiz/<int:id>/eliminar-opcion/', views.course_quiz_option_delete_view, name='curso_question_delete_option'),
    path('curso/quiz/calificar/<int:user_pk>/<int:quiz_pk>/<int:grade>/', views.course_quiz_grade, name='curso_quiz_grade'),


]

