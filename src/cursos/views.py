from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models import Q

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
    template_name = template_admin_pre + 'course_list.html'

    courses = Course.objects.all()
    context['courses'] = courses

    return render(request, template_name, context)


def adcourse_create_view(request):
    context = {}
    template_name = template_admin_pre + 'course_create_form.html'

    user = request.user
    extendedUser = user.extended_user

    course_form = CourseCreateForm()

    if request.method == 'POST':
        course_form = CourseCreateForm(request.POST)

        if course_form.is_valid():

            course = Course()

            course.name = course_form.cleaned_data['name']
            course.description = course_form.cleaned_data['description']
            course.date_created = date.today()
            course.owner = extendedUser

            course.save()

            return redirect(reverse('cursos:adcourse_detail', kwargs={'id': course.pk}))
        else:
            print(course_form.errors)

    context['form'] = course_form

    return render(request, template_name, context)


def adcourse_detail_view(request, id):
    context = {}
    template_name = template_admin_pre + 'course_detail.html'

    course = get_object_or_404(Course, pk=id)
    context['course'] = course

    return render(request, template_name, context)


def adcourse_members_view(request, id):
    context = {}
    template_name = template_admin_pre + 'course_members.html'

    course = get_object_or_404(Course, pk=id)

    members = MemberOf.objects.filter(course=course)

    context['course'] = course
    context['members'] = members

    return render(request, template_name, context)


def adcourse_addmember_view(request, id):
    context = {}
    template_name = template_admin_pre + 'course_add_member.html'

    course = get_object_or_404(Course, pk=id)

    users = ExtendedUser.objects.filter(~Q(courses__course=course))
    context['users'] = users

    course = get_object_or_404(Course, pk=id)

    return render(request, template_name)


def adcourse_addingmember_view(request, id, user_id):

    course = get_object_or_404(Course, pk=id)
    user = get_object_or_404(User, pk=user_id)

    try:
        membership = MemberOf(
                member=user,
                course=course,
                dateJoined=date.today()
            )
        membership.save()
    except:
        print('No se pudo')
    
    return redirect(reverse('cursos:adcourse_add_members', kwargs={'id':course.pk}))



def adcourse_delete_view(request, id):
    context = {}
    template_name = template_admin_pre + 'course_delete.html'

    course = get_object_or_404(Course, pk=id)

    if request.method == 'POST':
        course.delete()
        return redirect(reverse('index'))

    context['course'] = course

    return render(request, template_name, context)





def menu(request):
    return render(request, 'cursos/menu.html')

def course(request):
    return render(request, 'cursos/course.html')