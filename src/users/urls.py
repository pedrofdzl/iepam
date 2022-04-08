from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('', views.user_list_view, name='users_list'),
    path('login/', views.user_login_view, name='user_login'),
    path('register/', views.user_register_view, name='user_create'),
    path('user-detail/<int:id>/', views.user_detail_view, name='user_profile'),
    path('user-detail/<int:id>/update/', views.user_update_view, name='user_update'),
]