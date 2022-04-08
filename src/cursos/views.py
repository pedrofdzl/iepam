from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import get_user_model

from datetime import date

from .models import Course, MemberOf
from .forms import CourseCreateForm
from users.models import ExtendedUser

User = get_user_model()

# Create your views here.


template_prefix = 'courses/'
template_admin_pre = template_prefix + 'admin/'

############################
######## Admin Views #######
############################

def adcourse_list_view(request):
    context = {}
    template_name = ''

    courses = Course.objects.all()
    context['courses'] = courses

    return render(request, template_name, context)


def adcourse_create_view(request):
    context = {}
    template_name = ''

    course_form = CourseCreateForm()

    if request.method == 'POST':
        course_form = CourseCreateForm(request.POST)

        if course_form.is_valid():
            

            course = Course()

            course.name = course_form.cleaned_data['name']
            course.description = course_form.cleaned_data['description']
            course.date_created = date.today()
            course.owner = request.user

            course.save()
        else:
            print(course_form.errors)

    context['form'] = course_form

    return render(request, template_name, context)


def adcourse_detail_view(request, id):
    context = {}
    template_name = ''

    course = get_object_or_404(Course, pk=id)
    context['course'] = course

    return render(request, template_name, context)


def adcourse_members_view(request, id):
    context = {}
    template_name = ''

    course = get_object_or_404(Course, pk=id)

    members = MemberOf.objects.filter(course=course)

    context['course'] = course
    context['members'] = members

    return render(request, template_name, context)


def adcourse_addmember_view(request, id):
    context = {}
    template_name = ''

    

    course = get_object_or_404(Course, pk=id)



def adcourse_addingmember_view(request, id, user_id):
    context = {}
    template_name = ''

    course = get_object_or_404(Course, pk=id)
    user = get_object_or_404(User, pk=user_id)

    try:
        membership = MemberOf(
                member=user,
                course=course,
                dateJoined=date.today()
            )
    except:
        print('No se pudo')
    
    # return redirect()


def menu(request):
    return render(request, 'cursos/menu.html')

def course(request):
    return render(request, 'cursos/course.html')