from django.shortcuts import render, redirect
from django.urls import reverse

from users.models import ExtendedUser
from cursos.models import Course

# Create your views here.

def index(request):
    context = {}

    if not request.user.is_authenticated:
        return redirect(reverse('users:login'))

    user = request.user

    context["user"] = user

    return render(request, 'index.html',  context)


def panel(request):
    context = {}

    courses = Course.objects.all()
    users = ExtendedUser.objects.all()


    context['users'] = users
    context['courses'] = courses

    return render(request, 'admin.html', context)