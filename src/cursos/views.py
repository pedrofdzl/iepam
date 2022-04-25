from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.db.models import Q

from datetime import date

from .models import Course, Entrega, MemberOf, Modulo, Lectura, Actividad, Video, Quiz
from .forms import CourseCreateForm, EntregaAddForm, LectureAddForm, ModuleAddForm, ActivityAddForm, VideoAddForm
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


def adcourse_edit_view(request, id):
    context = {}
    template_name = template_admin_pre + 'course_edit_form.html'

    course = get_object_or_404(Course, pk=id)

    if request.method == 'GET':
        course_form = CourseCreateForm(instance=course)

    if request.method == 'POST':
        course_form = CourseCreateForm(request.POST, instance=course)

        if course_form.is_valid():

            course.save()

            return redirect(reverse('cursos:course_detail', kwargs={'id': course.pk}))
        else:
            print(course_form.errors)

    context['form'] = course_form
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
    user = request.user
    context = {}
    template_name = template_prefix + 'course.html'

    course = get_object_or_404(Course, pk=id)
    modules = Modulo.objects.filter(curso=id)

    # Calculo de actividades totales para el progreso
    total_items = 0
    completed_items = 0
    completion_ratio = 0
    completion_percentage = 0
    
    for module in modules:

        total_items += module.lecturas.all().count()
        for lecture in module.lecturas.all():
            if lecture.reads.filter(pk=user.pk).exists():
                completed_items += 1

        total_items += module.videos.all().count()
        for video in module.videos.all():
            if video.watches.filter(pk=user.pk).exists():
                completed_items += 1

    if total_items > 0:
        completion_ratio = completed_items / total_items
        completion_percentage = int(completion_ratio * 100)

    liked = False

    if user.is_authenticated:
        if user.likes.filter(pk=id).exists():
            liked = True

    context['liked'] = liked
    context['course'] = course
    context['modules'] = modules
    context['total_items'] = total_items
    context['completed_items'] = completed_items
    context['completion_ratio'] = completion_ratio
    context['completion_percentage'] = completion_percentage

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


def like_curso(request, id):
    curso = get_object_or_404(Course, pk=id)
    
    liked = False
    if curso.likes.filter(id=request.user.id).exists():
        curso.likes.remove(request.user)
        liked = False
    else:
        curso.likes.add(request.user)
        liked = True

    return redirect(reverse('cursos:course_detail', kwargs={'id': curso.pk}))


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

def course_edit_module_view(request, id):
    context = {}
    template_name = template_prefix + 'course_edit_module.html'

    module = get_object_or_404(Modulo, pk=id)
    
    if request.method == 'GET':
        module_form = ModuleAddForm(instance=module)

    if request.method == 'POST':
        module_form = ModuleAddForm(request.POST, instance=module)

        if module_form.is_valid():

            module.save()

            return redirect(reverse('cursos:course_detail', kwargs={'id': module.curso.pk}))
        else:
            print(module_form.errors)

    context['module'] = module
    context['course'] = module.curso
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
                lecture.content = lecture_form.cleaned_data['content']
                lecture.author = lecture_form.cleaned_data['author']
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
                activity.instructions = activity_form.cleaned_data['instructions']
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
                video.url = youtube_url_to_embed(video_form.cleaned_data['url'])
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

def course_edit_item_view(request, id, action):
    context = {}
    template_name = template_prefix + 'course_edit_item.html'

    if (action == 1):
        stuff = get_object_or_404(Lectura, pk=id)
    if (action == 2):
        stuff = get_object_or_404(Actividad, pk=id)
    if (action == 3):
        stuff = get_object_or_404(Video, pk=id)

    lecture_form = LectureAddForm()
    activity_form = ActivityAddForm()
    video_form = VideoAddForm()

    if request.method == 'GET':
        if (action == 1):
            lecture_form = LectureAddForm(instance=stuff)
        if (action == 2):
            activity_form = ActivityAddForm(instance=stuff)
        if (action == 3):
            video_form = VideoAddForm(instance=stuff)

    if request.method == 'POST':
        if action == 1:
            lecture_form = LectureAddForm(request.POST, instance=stuff)

            if lecture_form.is_valid():

                stuff.save()

                return redirect(reverse('cursos:course_detail', kwargs={'id': stuff.modulo.curso.pk}))
            else:
                print(lecture_form.errors)
        if action == 2:
            activity_form = ActivityAddForm(request.POST, instance=stuff)

            if activity_form.is_valid():

                stuff.save()

                return redirect(reverse('cursos:course_detail', kwargs={'id': stuff.modulo.curso.pk}))
            else:
                print(activity_form.errors)
        if action == 3:
            video_form = VideoAddForm(request.POST, instance=stuff)

            if video_form.is_valid():

                stuff.url = youtube_url_to_embed(video_form.cleaned_data['url'])
                stuff.save()

                return redirect(reverse('cursos:course_detail', kwargs={'id': stuff.modulo.curso.pk}))
            else:
                print(video_form.errors)

    context['modulo'] = stuff.modulo
    context['lec_form'] = lecture_form
    context['act_form'] = activity_form
    context['vid_form'] = video_form
    context['action'] = action

    return render(request, template_name, context)

def youtube_url_to_embed(link):
    video_code = link[-11:]
    embed_template = "https://www.youtube.com/embed/"
    return embed_template + video_code


def course_lecture_view(request, id):
    user = request.user
    context = {}
    template_name = template_prefix + 'lecture.html'

    lecture = get_object_or_404(Lectura, pk=id)
    course = lecture.modulo.curso

    viewed = False

    if user.is_authenticated:
        if user.read_lectures.filter(pk=id).exists():
            viewed = True

    context['viewed'] = viewed
    context['lecture'] = lecture
    context['course'] = course

    return render(request, template_name, context)


def read_lecture(request, id):
    lecture = get_object_or_404(Lectura, pk=id)
    
    liked = False
    if lecture.reads.filter(id=request.user.id).exists():
        lecture.reads.remove(request.user)
        liked = False
    else:
        lecture.reads.add(request.user)
        liked = True

    return redirect(reverse('cursos:course_lecture', kwargs={'id': lecture.pk}))


def course_activity_view(request, id):
    context = {}
    template_name = template_prefix + 'activity.html'

    activity = get_object_or_404(Actividad, pk=id)
    course = activity.modulo.curso

    entrega_form = EntregaAddForm()

    if request.method == 'POST':
        entrega_form = EntregaAddForm(request.POST)

        if entrega_form.is_valid():

            entrega = Entrega()

            entrega.file = entrega_form.cleaned_data['file']
            entrega.actividad = activity
            entrega.user = request.user.extended_user
            entrega.grade = -1

            entrega.save()

            return redirect(reverse('cursos:course_detail', kwargs={'id': activity.modulo.curso.pk}))
        else:
            print(entrega_form.errors)

    context['activity'] = activity
    context['entrega_form'] = entrega_form
    context['course'] = course

    return render(request, template_name, context)


def course_video_view(request, id):
    user = request.user
    context = {}
    template_name = template_prefix + 'video.html'

    video = get_object_or_404(Video, pk=id)
    course = video.modulo.curso

    viewed = False

    if user.is_authenticated:
        if user.watched_videos.filter(pk=id).exists():
            viewed = True

    context['viewed'] = viewed
    context['video'] = video
    context['course'] = course

    return render(request, template_name, context)


def watch_video(request, id):
    video = get_object_or_404(Video, pk=id)
    
    liked = False
    if video.reads.filter(id=request.user.id).exists():
        video.reads.remove(request.user)
        liked = False
    else:
        video.reads.add(request.user)
        liked = True

    return redirect(reverse('cursos:course_video', kwargs={'id': video.pk}))


def watch_video(request, id):
    video = get_object_or_404(Video, pk=id)
    
    liked = False
    if video.watches.filter(id=request.user.id).exists():
        video.watches.remove(request.user)
        liked = False
    else:
        video.watches.add(request.user)
        liked = True

    return redirect(reverse('cursos:course_video', kwargs={'id': video.pk}))