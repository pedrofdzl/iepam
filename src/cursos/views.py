from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import Http404, FileResponse
from django.contrib.auth import get_user_model
from django.db.models import Q

from django.contrib.auth.decorators import login_required, permission_required

from datetime import date
from django.utils import timezone
import os

from .models import Course, Entrega, MemberOf, Modulo, Lectura, Actividad, Question, Video, Quiz, QuestionOption, QuizResult
from .forms import (
                    CourseCreateForm, EntregaAddForm, LectureAddForm, 
                    ModuleAddForm, ActivityAddForm, VideoAddForm,
                    QuizForm, QuestionForm, QuestionOptionsForm
                )
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

    if request.user.extended_user == course.owner:
        context['is_owner'] = True

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
        if request.META['HTTP_REFERER']:
            return redirect(request.META['HTTP_REFERER'])
        return redirect(reverse('cursos:adcourse_members', kwargs={'id':course.pk}))

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
    context['total_items'] = total_items
    context['completed_items'] = completed_items
    context['completion_ratio'] = completion_ratio
    context['completion_percentage'] = completion_percentage

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

    # Quiz forms
    quiz_form = QuizForm()

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

        if action == 4:
            quiz_form = QuizForm(request.POST)

            if quiz_form.is_valid():
                quiz = quiz_form.save(commit=False)
                quiz.modulo = modulo
                quiz.save()

                return redirect(reverse('cursos:course_quiz', kwargs={'id':quiz.pk}))
            else:
                print(quiz_form.errorr)

    context['modulo'] = modulo
    context['lec_form'] = lecture_form
    context['act_form'] = activity_form
    context['vid_form'] = video_form
    context['quiz_form'] = quiz_form
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
def course_quiz_view(request, id):
    user = request.user
    extended_user = user.extended_user
    context = {}
    template_name = template_prefix + 'quiz.html'

    quiz = get_object_or_404(Quiz, pk=id)
    course = quiz.modulo.curso

    questions = quiz.questions.all()



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

    context['course'] = quiz.modulo.curso
    context['is_owner'] = is_owner
    context['is_member'] = is_member
    context['liked'] = liked
    # end of side panel

    context['quiz'] = quiz
    context['questions'] = questions

    return render(request, template_name, context)



def course_quiz_delete_view(request, id):
    user = request.user
    extended_user = user.extended_user
    context = {}
    template_name = template_prefix + 'quiz_confirm_delete.html'

    quiz = get_object_or_404(Quiz, pk=id)
    course = quiz.modulo.curso

    
    if request.method == 'POST':
        quiz.delete()
        return redirect(reverse('cursos:course_detail', kwargs={'id':course.pk}))


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

    context['quiz'] = quiz

    return render(request, template_name, context)



@login_required
def course_quiz_create_question_view(request, id):
    user = request.user
    extended_user = user.extended_user
    context = {}
    template_name = template_prefix + 'quiz_question_form.html'

    quiz = get_object_or_404(Quiz, pk=id)
    course = quiz.modulo.curso


    question_form = QuestionForm()

    if request.method == 'POST':
        question_form = QuestionForm(request.POST)

        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()

            return redirect(reverse('cursos:curso_question_add_option', kwargs={'id': question.pk}))
        else:
            print(question_form.errors)

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

    context['quiz'] = quiz
    context['form'] = question_form

    return render(request, template_name, context)


def course_quiz_grade(request, user_pk, quiz_pk, grade):

    extended_user = get_object_or_404(ExtendedUser, pk=user_pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)

    if QuizResult.objects.filter(quiz=quiz, user=extended_user).exists():
        result = QuizResult.objects.filter(quiz=quiz, user=extended_user).first()
        if result.grade < grade:
            result.grade = grade
            result.save()
    else:
        result = QuizResult()

        result.user = extended_user
        result.quiz = quiz
        result.grade = int(grade)

    return redirect(reverse('cursos:course_detail', kwargs={'id': quiz.modulo.curso.pk}))

    


@login_required
def course_quiz_delete_question_view(request, id):
    question = get_object_or_404(Question, pk=id)
    quiz = question.quiz
    question.delete()

    return redirect(reverse('cursos:course_quiz', kwargs={'id': quiz.pk}))


@login_required
def course_quiz_update_question_view(request, id):
    user = request.user
    extended_user = user.extended_user
    context = {}
    template_name = template_prefix + 'quiz_question_form.html'

    question = get_object_or_404(Question, pk=id)
    quiz = question.quiz
    modulo = quiz.modulo
    course = modulo.curso


    question_form = QuestionForm(instance=question)

    if request.method == 'POST':
        question_form = QuestionForm(request.POST, instance=question)

        if question_form.is_valid():
            question = question_form.save()

            return redirect(reverse('cursos:course_quiz_edit_question', kwargs={'id': question.pk}))
        else:
            print(question_form.errors)

    context['form'] = question_form
    context['quiz'] = quiz
    context['editing'] = True
    context['question'] = question


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



def course_quiz_option_create_view(request, id):
    user = request.user
    extended_user = user.extended_user
    context = {}
    template_name = template_prefix + 'quiz_questionoption_form.html'


    question = get_object_or_404(Question, pk=id)
    quiz = question.quiz
    modulo = quiz.modulo
    course = modulo.curso


    option_form = QuestionOptionsForm()

    if request.method == 'POST':
        option_form = QuestionOptionsForm(request.POST)
        option_form.instance.question = question

        if option_form.is_valid():
            option = option_form.save(commit=False)
            # option.question = question
            option.save()
            return redirect(reverse('cursos:course_quiz_edit_question', kwargs={'id': question.pk}))
        else:
            print(option_form.errors)

    context['form'] = option_form
    context['quiz'] = quiz
    context['question'] = question


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



def course_quiz_option_update_view(request, id):
    user = request.user
    extended_user = user.extended_user
    context = {}
    template_name = template_prefix + 'quiz_questionoption_form.html'

    option = get_object_or_404(QuestionOption, pk=id)
    question = option.question
    quiz = question.quiz
    modulo = quiz.modulo
    course = modulo.curso


    option_form = QuestionOptionsForm(instance=option)

    if request.method == 'POST':
        option_form = QuestionOptionsForm(request.POST, instance=option)

        if option_form.is_valid():
            option = option_form.save(commit=False)
            option.question = question
            option.save()
            return redirect(reverse('cursos:course_quiz_edit_question', kwargs={'id': question.pk}))

        else:
            print(option_form.errors)
    
    context['editing'] = True
    context['form'] = option_form
    context['quiz'] = quiz
    context['question'] = question
    context['editing'] = True


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
def course_quiz_option_delete_view(request, id):
    option = get_object_or_404(QuestionOption, pk=id)
    question = option.question

    option.delete()
    return redirect(reverse('cursos:course_quiz_edit_question', kwargs={'id': question.pk}))

@login_required
def course_lecture_view(request, id):
    user = request.user
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

    viewed = False

    if user.is_authenticated:
        if user.read_lectures.filter(pk=id).exists():
            viewed = True

    context['viewed'] = viewed
    context['lecture'] = lecture
    context['course'] = course

    return render(request, template_name, context)


def course_lecture_delete_view(request, id):
    user = request.user
    context = {}
    template_name = template_prefix + 'lecture_confirm_delete.html'

    user = request.user
    extended_user = user.extended_user

    lecture = get_object_or_404(Lectura, pk=id)
    course = lecture.modulo.curso


    if request.method == 'POST':
        lecture.delete()
        return redirect(reverse('cursos:course_detail', kwargs={'id':course.pk}))


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




@login_required
def course_activity_view(request, id):
    context = {}
    template_name = template_prefix + 'activity.html'
    user = request.user
    extended_user = user.extended_user

    activity = get_object_or_404(Actividad, pk=id)
    course = activity.modulo.curso
    submited = False

    if Entrega.objects.filter(user=extended_user, actividad=activity).exists():
        # print('hey')
        entry = Entrega.objects.filter(user=extended_user, actividad=activity).first()
        context['entry'] = entry
        submited = True

    entrega_form = EntregaAddForm()

    if request.method == 'POST' and not submited:
        entrega_form = EntregaAddForm(request.POST, files=request.FILES)

        if entrega_form.is_valid():

            entrega = Entrega()
            

            if 'file' in request.FILES:
                entrega.file = entrega_form.cleaned_data['file']

            entrega.actividad = activity
            entrega.user = request.user.extended_user
            entrega.created_date = timezone.now()

            entrega.save()

            # submited = True
            return redirect(reverse('cursos:course_activity', kwargs={'id': activity.pk}))
        else:
            print(entrega_form.errors)

    context['activity'] = activity
    context['entrega_form'] = entrega_form
    context['course'] = course
    context['submited'] = submited

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

def course_activity_delete_view(request, id):
    context = {}
    template_name = template_prefix + 'activity_confirm_delete.html'
    user = request.user
    extended_user = user.extended_user

    activity = get_object_or_404(Actividad, pk=id)
    course = activity.modulo.curso


    if request.method == 'POST':
        activity.delete()
        return redirect(reverse('cursos:course_detail', kwargs={'id': course.pk}))
   

    context['activity'] = activity
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


def course_activity_entry_detail_view(request, id):
    context = {}
    template_name = template_prefix + 'activity_entry.html'
    user = request.user
    extended_user = user.extended_user

    entry = get_object_or_404(Entrega, pk=id)
    activity = entry.actividad
    course = activity.modulo.curso
    valid = False

    if request.method == 'POST':
        try:
            grade = int(request.POST.get('grade'))
            valid = True
        except:
            context['error_message'] = 'No es un valor valido' 
        
        if valid and 0 <= grade <= 100:
            entry.grade = grade
            entry.save()

            return redirect(reverse('cursos:course_activity_entry', kwargs={'id': entry.pk}))

        else:
            context['error_message'] = 'No es un valor valido' 

    context['activity'] = activity
    context['entry'] = entry
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


def course_activity_entry_file_view(request, id):
    entry = get_object_or_404(Entrega, pk=id)

    if os.path.exists(entry.file.path):
        return FileResponse(open(entry.file.path, 'rb'), as_attachment=True)
    return Http404('No hay archivo disponible')



def course_activity_entry_delete_view(request, id):
    context = {}
    template_name = template_prefix + 'activity_entry_delete.html'
    user = request.user
    extended_user = user.extended_user

    entry = get_object_or_404(Entrega, pk=id)
    activity = entry.actividad
    course = activity.modulo.curso

    if request.method == 'POST':
        entry.delete()
        return redirect(reverse('cursos:course_activity', kwargs={'id': activity.pk}))


    context['activity'] = activity
    context['entry'] = entry
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
    user = request.user
    context = {}
    template_name = template_prefix + 'video.html'
    user = request.user
    extended_user = user.extended_user

    video = get_object_or_404(Video, pk=id)
    course = video.modulo.curso

    viewed = False

    if user.is_authenticated:
        if user.watched_videos.filter(pk=id).exists():
            viewed = True

    context['viewed'] = viewed
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


def course_video_delete_view(request, id):
    user = request.user
    context = {}
    template_name = template_prefix + 'video_confirm_delete.html'

    user = request.user
    extended_user = user.extended_user

    video = get_object_or_404(Video, pk=id)
    course = video.modulo.curso


    if request.method == 'POST':
        video.delete()
        return redirect(reverse('cursos:course_detail', kwargs={'id':course.pk}))


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

    viewed = False

    if user.is_authenticated:
        if user.read_lectures.filter(pk=id).exists():
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
