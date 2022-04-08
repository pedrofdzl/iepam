from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('', views.user_list_view, name='users_list'),
    path('register/', views.aduser_member_register_View, name='user_create'),
    path('user-detail/<int:id>/', views.aduser_detail_view, name='user_profile'),
    path('user-detail/<int:id>/update/', views.aduser_update_view, name='user_update'),
    path('user-detail/<int:id>/deactivate/', views.aduser_deactivate_view, name='user_deactivate'),

    path('profile/', views.memuser_profile_view, name='user_profile'),
    path('profile/update/', views.memuser_update_view, name='user_profile_update'),
    path('profile/update/cv/', views.memuser_changeCV_view, name='user_profile_updateCV'),
]