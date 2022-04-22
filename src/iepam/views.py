from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required

from users.models import ExtendedUser
from cursos.models import Course
from django.urls import reverse

# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')


@login_required
@permission_required(['users.is_admin'], raise_exception=True)
def panel(request):
    context = {}

    courses = Course.objects.all()
    users = ExtendedUser.objects.all()


    context['users'] = users
    context['courses'] = courses


    if request.method == 'GET':
        username = request.GET.get('usuario')
        courses = request.GET.get('courses')

        if username:
            found_users = ExtendedUser.objects.filter(
                    Q(user__username__contains=username) |
                    Q(user__first_name__contains=username) |
                    Q(user__last_name__contains=username) | 
                    Q(second_last_name__contains=username)
                )

            context['users'] = found_users

        if courses:
            found_courses = Course.objects.filter(name__contains=courses)

            context['courses'] = found_courses


    return render(request, 'admin.html', context)