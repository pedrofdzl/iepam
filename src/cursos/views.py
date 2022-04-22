from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models import Q

from datetime import date

from .models import Course, MemberOf, Modulo, Lectura, Actividad, Video, Quiz
from .forms import CourseCreateForm, LectureAddForm, ModuleAddForm, ActivityAddForm, VideoAddForm
from users.models import ExtendedUser

User = get_user_model()

# Create your views here.


template_prefix = 'cursos/'
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

            return redirect(reverse('cursos:course_detail', kwargs={'id': course.pk}))
        else:
            print(course_form.errors)

    context['form'] = course_form

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

    users = ExtendedUser.objects.filter(~Q(courses__course=course)).exclude(Q(own_courses=course))
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


def course_detail_view(request, id):
    context = {}
    template_name = template_prefix + 'course.html'

    course = get_object_or_404(Course, pk=id)
    modules = Modulo.objects.filter(curso=id)

    context['course'] = course
    context['modules'] = modules

    return render(request, template_name, context)


############################
######## Member Views #######
############################



def menu(request):
    context = {}
    template_name = template_prefix + 'menu.html'

    cursos = Course.objects.all()

    context['cursos'] = cursos

    return render(request, template_name, context)


def course_create_module_view(request, id):
    context = {}
    template_name = template_prefix + 'course_create_module.html'

    course = get_object_or_404(Course, pk=id)

    module_form = ModuleAddForm()

    if request.method == 'POST':
        module_form = ModuleAddForm(request.POST)

        if module_form.is_valid():

            module = Modulo()

            module.name = module_form.cleaned_data['name']
            module.curso = course

            module.save()

            return redirect(reverse('cursos:course_detail', kwargs={'id': course.pk}))
        else:
            print(module_form.errors)

    context['course'] = course
    context['form'] = module_form

    return render(request, template_name, context)


def course_create_item_view(request, id, action):
    context = {}
    template_name = template_prefix + 'course_create_item.html'

    modulo = get_object_or_404(Modulo, pk=id)

    lecture_form = LectureAddForm()
    activity_form = ActivityAddForm()
    video_form = VideoAddForm()

    if request.method == 'POST':
        if action == 1:
            lecture_form = LectureAddForm(request.POST)

            if lecture_form.is_valid():

                lecture = Lectura()

                lecture.name = lecture_form.cleaned_data['name']
                lecture.description = lecture_form.cleaned_data['description']
                lecture.modulo = modulo

                lecture.save()

                return redirect(reverse('cursos:course_detail', kwargs={'id': modulo.curso.pk}))
            else:
                print(lecture_form.errors)
        if action == 2:
            activity_form = ActivityAddForm(request.POST)

            if activity_form.is_valid():

                activity = Actividad()

                activity.name = activity_form.cleaned_data['name']
                activity.description = activity_form.cleaned_data['description']
                activity.modulo = modulo

                activity.save()

                return redirect(reverse('cursos:course_detail', kwargs={'id': modulo.curso.pk}))
            else:
                print(activity_form.errors)
        if action == 3:
            video_form = VideoAddForm(request.POST)

            if video_form.is_valid():

                video = Video()

                video.name = video_form.cleaned_data['name']
                video.description = video_form.cleaned_data['description']
                video.url = video_form.cleaned_data['url']
                video.modulo = modulo

                video.save()

                return redirect(reverse('cursos:course_detail', kwargs={'id': modulo.curso.pk}))
            else:
                print(video_form.errors)

    context['modulo'] = modulo
    context['lec_form'] = lecture_form
    context['act_form'] = activity_form
    context['vid_form'] = video_form
    context['action'] = action

    return render(request, template_name, context)

    
