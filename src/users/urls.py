from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [

    path('login/', views.user_login_view, name='login'),
    path('logout/', views.user_logout_view, name='logout'),


    path('', views.aduser_list_view, name='users_list'),
    
    # Admin views
    path('register/', views.aduser_member_register_View, name='user_create'),
    path('user-detail/<int:id>/', views.aduser_detail_view, name='user_detail'),
    path('user-detail/<int:id>/cv/', views.user_get_cv_view, name='user_cv'),
    path('user-detail/<int:id>/update/', views.aduser_update_view, name='user_update'),
    path('user-detail/<int:id>/update/cv/', views.aduser_change_cv, name='user_update_cv'),
    path('user-detail/<int:id>/update/profile-pic/', views.aduser_change_profilepic_view, name='user_update_profilepic'),
    path('user-detail/<int:id>/update/cambiar-grupo/', views.aduser_change_group, name='user_change_group'),

    path('user-detail/<int:id>/deactivate/', views.aduser_deactivate_view, name='user_deactivate'),
    path('user-detail/<int:id>/activate/', views.aduser_activate_view, name='user_activate'),

    # Profile views
    path('profile/', views.memuser_profile_view, name='user_profile'),
    path('profile/update/', views.memuser_update_view, name='user_profile_update'),
    path('profile/update/cv/', views.memuser_changeCV_view, name='user_profile_updateCV'),
    path('profile/update/profile-pic/', views.memuser_change_profilepic_view, name='user_profile_updatepic'),
]