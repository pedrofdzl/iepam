from datetime import datetime
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from iepam.extras import get_dashboard_context

from users.models import ExtendedUser
from cursos.models import Course

from django.http import Http404, HttpResponseServerError
from django.core.exceptions import PermissionDenied

# Create your views here.
@login_required
def index(request):
    context = {}

    dateToday = datetime.now()

    context['date'] = dateToday

    context = get_dashboard_context(request, context)

    return render(request, 'index.html', context)


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


# Test views

# 404 VIEW
def my404_view(request):
    raise Http404()

# 403 View
def my403_view(request):
    raise PermissionDenied()

# 500 View
def my500_view(request):
    raise HttpResponseServerError()
