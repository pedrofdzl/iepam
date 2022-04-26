from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import Http404
from django.contrib.auth import get_user_model
from django.db.models import Q

from django.contrib.auth.decorators import login_required, permission_required

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

@login_required
@permission_required(['users.is_teacher'], raise_exception=True)
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

@login_required
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


@login_required
def adcourse_members_view(request, id):
    context = {}
    template_name = template_admin_pre + 'course_members.html'

    course = get_object_or_404(Course, pk=id)

    # Get course members and non-members users
    members = MemberOf.objects.filter(course=course)
    not_members = ExtendedUser.objects.filter(~Q(courses__course=course)).exclude(Q(own_courses=course))


    if request.user.has_perm('users.is_admin'):
        if request.method == 'GET':
            username = request.GET.get('nombre')

            if username:
                not_members = not_members.filter(
                    Q(user__first_name__contains=username) |
                    Q(user__last_name__contains=username) |
                    Q(second_last_name__contains=username) 
                    # Q(user__username__contains=username)
                )

    context['course'] = course
    context['members'] = members
    context['not_members'] = not_members

    return render(request, template_name, context)


@login_required
def adcourse_addmember_view(request, id):
    context = {}
    template_name = template_admin_pre + 'course_add_member.html'

    course = get_object_or_404(Course, pk=id)

    members = ExtendedUser.objects.filter(~Q(courses__course=course)).exclude(Q(own_courses=course))
    # print(members)
    context['members'] = members
    context['course'] = course


    return render(request, template_name, context)


@login_required
def adcourse_addingmember_view(request, id, user_id):

    course = get_object_or_404(Course, pk=id)
    user = get_object_or_404(User, pk=user_id)
    extended_user = user.extended_user

    if course.owner == extended_user:
        return redirect(reverse('cursos:adcourse_add_members', kwargs={'id':course.pk}))

    try:
        membership = MemberOf(
                member=extended_user,
                course=course,
                dateJoined=date.today()
            )
        membership.save()
    except:
        print('No se pudo')
    
    # return redirect(reverse('cursos:adcourse_add_members', kwargs={'id':course.pk}))

    if request.META['HTTP_REFERER']:
        return redirect(request.META['HTTP_REFERER'])
    return redirect(reverse('cursos:adcourse_members', kwargs={'id':course.pk}))


@login_required
def adcourse_removemember_view(request, id, user_id):
    template_name = ''
    context = {}

    course = get_object_or_404(Course, pk=id)
    user = get_object_or_404(User, pk=user_id)
    extended_user = user.extended_user

    membership = get_object_or_404(MemberOf, member=extended_user, course=course)


@login_required
def adcourse_delete_view(request, id):
    context = {}
    template_name = template_admin_pre + 'course_delete.html'

    course = get_object_or_404(Course, pk=id)

    if request.method == 'POST':
        course.delete()
        return redirect(reverse('index'))

    context['course'] = course

    return render(request, template_name, context)


@login_required
def course_detail_view(request, id):
    user = request.user
    extended_user = user.extended_user
    context = {}
    template_name = template_prefix + 'course.html'

    course = get_object_or_404(Course, pk=id)
    modules = Modulo.objects.filter(curso=id)

    # Side Panel Variables
    liked = False
    is_member = False
    is_owner = False

    if user.likes.filter(pk=id).exists():
        liked = True
    
    if MemberOf.objects.filter(course=course, member=extended_user).exists():
        is_member = True

    if extended_user == course.owner:
        is_owner = True

    context['is_owner'] = is_owner
    context['is_member'] = is_member
    context['liked'] = liked


    context['course'] = course
    context['modules'] = modules

    return render(request, template_name, context)


############################
######## Member Views #######
############################

@login_required
def menu(request):
    context = {}
    template_name = template_prefix + 'menu.html'
    user = request.user
    extended_user = user.extended_user


    cursos = Course.objects.all()

    if request.method == 'GET':
        courses_type = request.GET.get('cursos')
        course_name = request.GET.get('curso')


        if courses_type:
            if courses_type == 'No Tomado':
                cursos = Course.objects.filter(~Q(course_members__member=extended_user))
            elif courses_type == 'Cursando':
                cursos = Course.objects.filter(Q(course_members__status=courses_type) & Q(course_members__member=extended_user))
            elif courses_type == 'Completado':
                cursos = Course.objects.filter(Q(course_members__status=courses_type) & Q(course_members__member=extended_user))
        
        if course_name:
            cursos = Course.objects.filter(name__contains=course_name)


    context['cursos'] = cursos


    return render(request, template_name, context)


@login_required
def like_curso(request, id):
    curso = get_object_or_404(Course, pk=id)
    
    liked = False
    if curso.likes.filter(id=request.user.id).exists():
        curso.likes.remove(request.user)
        liked = False
    else:
        curso.likes.add(request.user)
        liked = True


    if request.META['HTTP_REFERER']:
        return redirect(request.META['HTTP_REFERER'])
    return redirect(reverse('cursos:course_detail', kwargs={'id': curso.pk}))


@login_required
def course_create_module_view(request, id):
    context = {}
    template_name = template_prefix + 'course_create_module.html'

    course = get_object_or_404(Course, pk=id)
    
    if course.owner != request.user.extended_user:
        raise Http404()

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


@login_required
def course_edit_module_view(request, id):
    context = {}
    template_name = template_prefix + 'course_edit_module.html'

    module = get_object_or_404(Modulo, pk=id)
    if module.curso.owner != request.user.extended_user:
        raise Http404()
    
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


@login_required
def course_create_item_view(request, id, action):
    context = {}
    template_name = template_prefix + 'course_create_item.html'

    modulo = get_object_or_404(Modulo, pk=id)
    if modulo.curso.owner != request.user.extended_user:
        raise Http404()

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


@login_required
def course_edit_item_view(request, id, action):
    context = {}
    template_name = template_prefix + 'course_edit_item.html'

    module = get_object_or_404(Modulo, pk=id)
    if module.curso.owner != request.user.extended_user:
        raise Http404()

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

@login_required
def course_lecture_view(request, id):
    context = {}
    template_name = template_prefix + 'lecture.html'

    user = request.user
    extended_user = user.extended_user

    lecture = get_object_or_404(Lectura, pk=id)
    course = lecture.modulo.curso

    # Side Panel Variables
    liked = False
    is_member = False
    is_owner = False

    if user.likes.filter(pk=id).exists():
        liked = True
    
    if MemberOf.objects.filter(course=course, member=extended_user).exists():
        is_member = True

    if extended_user == course.owner:
        is_owner = True

    context['is_owner'] = is_owner
    context['is_member'] = is_member
    context['liked'] = liked
    # end of side panel

    context['lecture'] = lecture
    context['course'] = course

    return render(request, template_name, context)


@login_required
def course_activity_view(request, id):
    context = {}
    template_name = template_prefix + 'activity.html'
    user = request.user
    extended_user = user.extended_user

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

    # Side Panel Variables
    liked = False
    is_member = False
    is_owner = False

    if user.likes.filter(pk=id).exists():
        liked = True
    
    if MemberOf.objects.filter(course=course, member=extended_user).exists():
        is_member = True

    if extended_user == course.owner:
        is_owner = True

    context['is_owner'] = is_owner
    context['is_member'] = is_member
    context['liked'] = liked
    # end of side panel



    return render(request, template_name, context)

@login_required
def course_video_view(request, id):
    context = {}
    template_name = template_prefix + 'video.html'
    user = request.user
    extended_user = user.extended_user

    video = get_object_or_404(Video, pk=id)
    course = video.modulo.curso

    context['video'] = video
    context['course'] = course

    # Side Panel Variables
    liked = False
    is_member = False
    is_owner = False

    if user.likes.filter(pk=id).exists():
        liked = True
    
    if MemberOf.objects.filter(course=course, member=extended_user).exists():
        is_member = True

    if extended_user == course.owner:
        is_owner = True

    context['is_owner'] = is_owner
    context['is_member'] = is_member
    context['liked'] = liked
    # end of side panel

    return render(request, template_name, context)