from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import Http404, FileResponse
from django.contrib.auth import get_user_model
from django.db.models import Q

import random

from .extras import side_panel_context, check_for_completion

from django.contrib.auth.decorators import login_required, permission_required

from datetime import date
from django.utils import timezone
import os

from .models import (
                        Course, Entrega, MemberOf, Modulo, 
                        Lectura, Actividad, PuzzleGame, Question, Video,
                        Quiz, QuestionOption, QuizResult,
                        FileResource, HangmanGame, HangmanOption, SopaGame,
                        SopaOption,
                    )
from .forms import (
                    CourseCreateForm, EntregaAddForm, HangmanOptionForm, LectureAddForm, 
                    ModuleAddForm, ActivityAddForm, VideoAddForm,
                    QuizForm, QuestionForm, QuestionOptionsForm, FileResourceForm,
                    HangmanForm, HangmanOption, SopaForm, SopaOptionForm,
                )

from .extras import get_iframe_url

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


def adcourse_members_remove_view(request, id, user_id):
    context = {}
    template_name = template_admin_pre + 'course_remove_member.html'

    course = get_object_or_404(Course, pk=id)
    user = get_object_or_404(User, pk=user_id)
    extended_user = user.extended_user

    if course.owner == extended_user:
        if request.META['HTTP_REFERER']:
            return redirect(request.META['HTTP_REFERER'])
        return redirect(reverse('cursos:adcourse_members', kwargs={'id':course.pk}))

    if MemberOf.objects.filter(course=course, member=extended_user).exists():
        if request.method == 'POST':
            membership = MemberOf.objects.filter(course=course,member=extended_user).first()
            
            read_lecture = user.read_lectures.filter(modulo__curso=course).first()
            entrega = Entrega.objects.filter(user=extended_user, actividad__modulo__curso=course).first()
            watched_video = user.watched_videos.filter(modulo__curso=course).first()
            watched_resource = user.viewed_resources.filter(modulo__curso=course).first()
            quiz_result = QuizResult.objects.filter(user=user.extended_user, quiz__modulo__curso=course).first()

            if read_lecture:
                user.read_lectures.remove(read_lecture)
            if watched_video:
                user.watched_videos.remove(watched_video)
            if watched_resource:
                user.viewed_resources.remove(watched_resource)
            
            if entrega:
                entrega.delete()
            
            if quiz_result:
                quiz_result.delete()

            membership.delete()

            return redirect(reverse('cursos:adcourse_members', kwargs={'id':course.pk}))



    else:
        if request.META['HTTP_REFERER']:
            return redirect(request.META['HTTP_REFERER'])
        return redirect(reverse('cursos:adcourse_members', kwargs={'id':course.pk}))


    context['course'] = course
    context['extended_user'] = extended_user

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

    entregas_user = user.extended_user.entregas
    turned_activities = []
    for entrega in entregas_user.all():
        turned_activities.append(entrega.actividad)

    results_user = user.extended_user.quiz_results
    answered_quizzes = []
    for result in results_user.all():
        answered_quizzes.append(result.quiz)

    hangmans_user = user.completed_hangmans
    completed_hangmans = []
    for hangman in hangmans_user.all():
        completed_hangmans.append(hangman)

    resources_user = user.viewed_resources
    viewed_resources = []
    for resource in resources_user.all():
        viewed_resources.append(resource)


    context['course'] = course
    context['modules'] = modules
    context['turned_activities'] = turned_activities
    context['answered_quizzes'] = answered_quizzes
    context['completed_hangmans'] = completed_hangmans
    context['viewed_resources'] = viewed_resources

    context = side_panel_context(context, user.pk, course.pk)

    is_member = False
    if MemberOf.objects.filter(course=course, member=extended_user).exists():
        is_member = True

    if is_member:
        check_for_completion(request, course.pk)

    return render(request, template_name, context)


def course_delete_view(request, id):
    user = request.user
    extended_user = user.extended_user
    context = {}
    template_name = template_prefix + 'course_confirm_delete.html'

    course = get_object_or_404(Course, pk=id)

    if request.method == 'POST':
        course.delete()
        return redirect(reverse('cursos:menu'))

    
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
    context['extended_user'] = extended_user

    return render(request, template_name, context)


def course_leave_view(request, id):
    context = {}
    template_name = template_prefix + 'course_leave.html'
    course = get_object_or_404(Course, pk=id)

    user = request.user
    extended_user = user.extended_user

    if MemberOf.objects.filter(course=course, member=extended_user).exists():
        if request.method == 'POST':
            membership = MemberOf.objects.filter(course=course,member=extended_user).first()
            
            read_lecture = user.read_lectures.filter(modulo__curso=course).first()
            entrega = Entrega.objects.filter(user=extended_user, actividad__modulo__curso=course).first()
            watched_video = user.watched_videos.filter(modulo__curso=course).first()
            watched_resource = user.viewed_resources.filter(modulo__curso=course).first()
            quiz_result = QuizResult.objects.filter(user=user.extended_user, quiz__modulo__curso=course).first()

            if read_lecture:
                user.read_lectures.remove(read_lecture)
            if watched_video:
                user.watched_videos.remove(watched_video)
            if watched_resource:
                user.viewed_resources.remove(watched_resource)
            
            if entrega:
                entrega.delete()
            
            if quiz_result:
                quiz_result.delete()

            membership.delete()

            return redirect(reverse('cursos:course_detail', kwargs={'id':course.pk}))

    else:
        if request.META['HTTP_REFERER']:
            return redirect(request.META['HTTP_REFERER'])
        return redirect(reverse('cursos:course_detail', kwargs={'id':course.pk}))


    context['course'] = course
    context['extended_user'] = extended_user


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
    quiz_form = QuizForm()
    resource_form = FileResourceForm()
    hangman_form = HangmanForm() 
    sopa_form = SopaForm()

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
                video.url = get_iframe_url(video_form.cleaned_data['url'])
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

        
        if action == 5:
            # print(request.FILES)
            resource_form = FileResourceForm(request.POST, files=request.FILES)

            if resource_form.is_valid():
                resource = resource_form.save(commit=False)
                resource.modulo  = modulo
                resource.save()
                
                
                return redirect(reverse('cursos:course_detail', kwargs={'id': modulo.curso.pk}))
            else:
                print(resource_form.errors)

        if action == 6:
            hangman_form = HangmanForm(request.POST)

            if hangman_form.is_valid():
                hangman_game = hangman_form.save(commit=False)
                hangman_game.modulo = modulo
                hangman_game.save()

                return redirect(reverse('cursos:course_hangman', kwargs={'id': hangman_game.pk}))
            else:
                print(hangman_form.errors)
        if action == 7:
            sopa_form = SopaForm(request.POST)

            if sopa_form.is_valid():
                sopa_game = sopa_form.save(commit=False)
                sopa_game.modulo = modulo
                sopa_game.save()

                return redirect(reverse('cursos:course_sopa', kwargs={'id': sopa_game.pk}))
            else:
                print(sopa_form.errors)
                


    context['modulo'] = modulo
    context['lec_form'] = lecture_form
    context['act_form'] = activity_form
    context['vid_form'] = video_form
    context['quiz_form'] = quiz_form
    context['resource_form'] = resource_form
    context['hangman_form'] = hangman_form
    context['sopa_form'] = sopa_form
    context['action'] = action

    return render(request, template_name, context)


@login_required
def course_edit_item_view(request, id, action):
    context = {}
    template_name = template_prefix + 'course_edit_item.html'


    if action == 1:
        stuff = get_object_or_404(Lectura, pk=id)
    if action == 2:
        stuff = get_object_or_404(Actividad, pk=id)
    if action == 3:
        stuff = get_object_or_404(Video, pk=id)
    if action == 4:
        stuff = get_object_or_404(Quiz, pk=id)
    if action == 5:
        stuff = get_object_or_404(FileResource, pk=id)

    lecture_form = LectureAddForm()
    activity_form = ActivityAddForm()
    video_form = VideoAddForm()
    resource_form = FileResourceForm()
    quiz_form = QuizForm()

    module = stuff.modulo
    if module.curso.owner != request.user.extended_user:
        raise Http404()

    if request.method == 'GET':
        if action == 1:
            lecture_form = LectureAddForm(instance=stuff)
        if action == 2:
            activity_form = ActivityAddForm(instance=stuff)
        if action == 3:
            video_form = VideoAddForm(instance=stuff)
        if action == 4:
            quiz_form = QuizForm(instance=stuff)
        if action == 5:
            resource_form = FileResourceForm(instance=stuff)

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

                stuff.url = get_iframe_url(video_form.cleaned_data['url'])
                stuff.save()

                return redirect(reverse('cursos:course_detail', kwargs={'id': stuff.modulo.curso.pk}))
            else:
                print(video_form.errors)

        if action == 4:
            quiz_form = QuizForm(request.POST, instance=stuff)

            if quiz_form.is_valid():

                stuff.save()

                return redirect(reverse('cursos:course_quiz', kwargs={'id':stuff.pk}))
            else:
                print(quiz_form.errors)

        if action == 5:
            stuff_resource_path = stuff.resource.path
            resource_form = FileResourceForm(request.POST, files=request.FILES, instance=stuff)

            if resource_form.is_valid():
                stuff = resource_form.save(commit=False)

                if stuff_resource_path != stuff.resource.path:
                    os.remove(stuff_resource_path)

                stuff.save()

                return redirect(reverse('cursos:course_detail', kwargs={'id': stuff.modulo.curso.pk}))
            else:
                print(resource_form.errors)

    context['modulo'] = stuff.modulo
    context['lec_form'] = lecture_form
    context['act_form'] = activity_form
    context['vid_form'] = video_form
    context['quiz_form'] = quiz_form
    context['resource_form'] = resource_form
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
    results = quiz.results.all().order_by('-grade')

    context['quiz'] = quiz
    context['questions'] = questions
    context['results'] = results
 
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

    context['quiz'] = quiz

    return render(request, template_name, context)



@login_required
def course_quiz_answer_view(request, id):
    user = request.user
    extended_user = user.extended_user
    context = {}
    template_name = template_prefix + 'quiz_answer.html'

    quiz = get_object_or_404(Quiz, pk=id)

    questions = quiz.questions.all()

    quizData = quiz.name + '|' + str(quiz.questions.all().count()) + '|'
    quizQuestions = Question.objects.filter(quiz=quiz.pk)
    for question in quizQuestions:
        quizData += str(question.options.all().count()) + '|'
    for question in quizQuestions:
        quizData += question.prompt + '|'
    for question in quizQuestions:
        correct = question.options.all().filter(correct=True)
        questionOptions = QuestionOption.objects.filter(question=question.pk)
        quizData += correct[0].prompt + '|'
        for option in questionOptions:
            if option != correct[0]:
                quizData += option.prompt + '|'
    quizData += str(quiz.pk) + '|'

    context['quizData'] = quizData
    context['quiz'] = quiz
    context['questions'] = questions

    return render(request, template_name, context)


@login_required
def course_quiz_submit_view(request, id, calif):
    user = request.user
    extended_user = user.extended_user
    context = {}
    template_name = template_prefix + 'quiz_submit.html'

    quiz = get_object_or_404(Quiz, pk=id)

    context['extended_user'] = extended_user
    context['quiz'] = quiz
    context['grade'] = calif

    return course_quiz_grade(request, user.pk, quiz.pk, calif)


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
        result.save()

    check_for_completion(request, quiz.modulo.curso.pk)

    return redirect(reverse('cursos:course_detail', kwargs={'id': quiz.modulo.curso.pk}))


@login_required
def course_quiz_answered_view(request, id):
    user = request.user
    extended_user = user.extended_user
    context = {}
    template_name = template_prefix + 'quiz_answered.html'

    quiz = get_object_or_404(Quiz, pk=id)
    course = quiz.modulo.curso
    modules = course.modulos.all()
    result = get_object_or_404(QuizResult, quiz=quiz.pk, user=user.pk)
    
    # Calificaciones (leaderboard)
    results = QuizResult.objects.all().filter(quiz=quiz.pk).order_by('-grade')
    counter = 0
    top_results = []
    while counter < 10 and counter < len(results):
        top_results.append(results[counter])
        top_results[counter].grade = int(top_results[counter].grade)
        counter += 1

    context['course'] = course
    context['user'] = extended_user
    context['quiz'] = quiz
    context['result'] = result
    context['grade'] = int(result.grade)
    context['top_results'] = top_results

    context = side_panel_context(context, user.pk, course.pk)

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


    context['quiz'] = quiz
    context['form'] = question_form

    return render(request, template_name, context)



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

            return redirect(reverse('cursos:course_quiz', kwargs={'id': question.quiz.pk}))
        else:
            print(question_form.errors)

    context['form'] = question_form
    context['quiz'] = quiz
    context['editing'] = True
    context['question'] = question

    return render(request, template_name, context)



@login_required
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

    return render(request, template_name, context)


@login_required
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

    lecture = get_object_or_404(Lectura, pk=id)
    course = lecture.modulo.curso

    viewed = False

    if user.is_authenticated:
        if user.read_lectures.filter(pk=id).exists():
            viewed = True

    context['viewed'] = viewed
    context['lecture'] = lecture
    context['course'] = course

    context = side_panel_context(context, user.pk, course.pk)

    return render(request, template_name, context)


@login_required
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


    viewed = False

    if user.is_authenticated:
        if user.read_lectures.filter(pk=id).exists():
            viewed = True

    context['viewed'] = viewed
    context['lecture'] = lecture
    context['course'] = course

    return render(request, template_name, context)



@login_required
def read_lecture(request, id):
    lecture = get_object_or_404(Lectura, pk=id)
    
    if lecture.reads.filter(id=request.user.id).exists():
        lecture.reads.remove(request.user)
    else:
        lecture.reads.add(request.user)

    check_for_completion(request, lecture.modulo.curso.pk)

    return redirect(reverse('cursos:course_lecture', kwargs={'id': lecture.pk}))


@login_required
def course_resource_view(request, id):
    context = {}
    template_name = template_prefix + 'resource.html'
    user = request.user
    extended_user = user.extended_user

    resource = get_object_or_404(FileResource, pk=id)
    course = resource.modulo.curso

    context['resource'] = resource

    context = side_panel_context(context, user.pk, course.pk)

    return render(request, template_name, context)



def course_resource_delete_view(request, id):
    context = {}
    template_name = template_prefix + 'resource_confirm_delete.html'
    user = request.user
    extended_user = user.extended_user

    resource = get_object_or_404(FileResource, pk=id)
    course = resource.modulo.curso

    context['resource'] = resource

    if request.method == 'POST':
        resource.delete()
        return redirect(reverse('cursos:course_detail', kwargs={'id': course.pk}))


    return render(request, template_name, context)


def course_resource_download_view(request, id):

    resource = get_object_or_404(FileResource, pk=id)
    course = resource.modulo.curso
    resource_path = resource.resource.path

    check_for_completion(request, resource.modulo.curso.pk)

    if os.path.exists(resource_path):

        if MemberOf.objects.filter(member=request.user.extended_user, course=course).exists():
            resource.reads.add(request.user)

        return FileResponse(resource.resource.open(mode='rb'), as_attachment=True)
    else:
        raise Http404()







@login_required
def course_activity_view(request, id):
    context = {}
    template_name = template_prefix + 'activity.html'
    user = request.user
    extended_user = user.extended_user

    activity = get_object_or_404(Actividad, pk=id)
    course = activity.modulo.curso
    modules = Modulo.objects.all().filter(curso=course.pk)
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

    context = side_panel_context(context, user.pk, course.pk)

    return render(request, template_name, context)


@login_required
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

    context = side_panel_context(context, user.pk, course.pk)

    return render(request, template_name, context)


@login_required
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

    context = side_panel_context(context, user.pk, course.pk)

    return render(request, template_name, context)


@login_required
def course_activity_entry_file_view(request, id):
    entry = get_object_or_404(Entrega, pk=id)

    if os.path.exists(entry.file.path):
        return FileResponse(open(entry.file.path, 'rb'), as_attachment=True)
    return Http404('No hay archivo disponible')


@login_required
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

    context = side_panel_context(context, user.pk, course.pk)

    return render(request, template_name, context)


def course_hangman_view(request, id):
    context = {}
    template_name = template_prefix + 'hangman.html'
    user = request.user
    extended_user = user.extended_user

    hangman = get_object_or_404(HangmanGame, pk=id)
    course = hangman.modulo.curso
    options = hangman.options.all()

    context['hangman'] = hangman
    context['course'] = course
    context['options'] = options

    context = side_panel_context(context, user.pk, course.pk)

    return render(request, template_name, context)


@login_required
def course_hangman_answer_view(request, id):
    user = request.user
    extended_user = user.extended_user
    context = {}
    template_name = template_prefix + 'hangman_answer.html'

    hangman = get_object_or_404(HangmanGame, pk=id)

    questions = hangman.options.all()

    quizData = str(questions.all().count()) + '|'
    quizQuestions = HangmanOption.objects.filter(game=hangman.pk)
    for question in quizQuestions:
        quizData += question.option + '|'
    for question in quizQuestions:
        if random.randint(0, 1) == 0:
            quizData += question.hint_1 + '|'
        else:
            quizData += question.hint_1 + '|'
    quizData += str(hangman.pk) + '|'

    context['quizData'] = quizData
    context['hangman'] = hangman
    context['questions'] = questions

    return render(request, template_name, context)


def course_hangman_complete_view(request, id):
    hangman = get_object_or_404(HangmanGame, pk=id)
    
    if not hangman.completions.filter(id=request.user.id).exists():
        hangman.completions.add(request.user)

    return redirect(reverse('cursos:course_detail', kwargs={'id': hangman.modulo.curso.pk}))


def course_hangman_delete_view(request, id):
    context = {}
    template_name = template_prefix + 'hangman_confirm_delete.html'
    user = request.user
    extended_user = user.extended_user

    hangman = get_object_or_404(HangmanGame, pk=id)
    course = hangman.modulo.curso

    if request.method == 'POST':
        hangman.delete()
        return redirect(reverse('cursos:course_detail', kwargs={'id': course.pk}))


    context['hangman'] = hangman
    context['course'] = course

    context = side_panel_context(context, user.pk, course.pk)

    return render(request, template_name, context)



def course_hangman_option_create_view(request, id):
    context = {}
    template_name = template_prefix + 'hangman_option_form.html'
    user = request.user
    extended_user = user.extended_user

    hangman = get_object_or_404(HangmanGame, pk=id)
    course = hangman.modulo.curso

    option_form = HangmanOptionForm()

    if request.method == 'POST':
        option_form = HangmanOptionForm(request.POST)

        if option_form.is_valid():
            option = option_form.save(commit=False)

            option.game = hangman
            option.save()

            return redirect(reverse('cursos:course_hangman', kwargs={'id': hangman.pk}))
        else:
            print(option_form.errors)
    

    context['option_form'] = option_form
    context['hangman'] = hangman
    context['course'] = course

    context = side_panel_context(context, user.pk, course.pk)

    return render(request, template_name, context)



def course_hangman_option_edit_view(request, id):
    context = {}
    template_name = template_prefix + 'hangman_option_form.html'
    user = request.user
    extended_user = user.extended_user

    option = get_object_or_404(HangmanOption, pk=id)
    hangman = option.game
    course = hangman.modulo.curso

    option_form = HangmanOptionForm(instance=option)


    if request.method == 'POST':
        option_form = HangmanOptionForm(request.POST, instance=option)

        if option_form.is_valid():
            option = option_form.save()

            return redirect(reverse('cursos:course_hangman', kwargs={'id': hangman.pk}))
        else:
            print(option_form.errors)
    

    context['option_form'] = option_form
    context['hangman'] = hangman
    context['course'] = course

    context = side_panel_context(context, user.pk, course.pk)

    return render(request, template_name, context)


def course_hangman_option_delete_view(request, id):
    option = get_object_or_404(HangmanOption, pk=id)
    hangman = option.game

    option.delete()
    return redirect(reverse('cursos:course_hangman', kwargs={'id': hangman.pk}))


def course_sopa_view(request, id):
    context = {}
    template_name = template_prefix + 'sopa.html'
    user = request.user
    extended_user = user.extended_user

    sopa = get_object_or_404(SopaGame, pk=id)
    course = sopa.modulo.curso
    options = sopa.options.all()

    context['sopa'] = sopa
    context['course'] = course
    context['options'] = options

    context = side_panel_context(context, user.pk, course.pk)

    return render(request, template_name, context)


def course_sopa_complete_view(request, id):
    context = {}
    template_name = template_prefix + 'sopa_answer.html'

    sopa = get_object_or_404(SopaGame, pk=id)
    
    if not sopa.completions.filter(id=request.user.id).exists():
        sopa.completions.add(request.user)

    context['sopa'] = sopa

    return render(request, template_name, context)


def course_sopa_delete_view(request, id):
    context = {}
    template_name = template_prefix + 'sopa_confirm_delete.html'
    user = request.user
    extended_user = user.extended_user

    sopa = get_object_or_404(SopaGame, pk=id)
    course = sopa.modulo.curso

    if request.method == 'POST':
        sopa.delete()
        return redirect(reverse('cursos:course_detail', kwargs={'id': course.pk}))


    context['sopa'] = sopa
    context['course'] = course

    context = side_panel_context(context, user.pk, course.pk)

    return render(request, template_name, context)



def course_sopa_option_create_view(request, id):
    context = {}
    template_name = template_prefix + 'sopa_option_form.html'
    user = request.user
    extended_user = user.extended_user

    sopa = get_object_or_404(SopaGame, pk=id)
    course = sopa.modulo.curso

    option_form = SopaOptionForm()

    if request.method == 'POST':
        option_form = SopaOptionForm(request.POST)

        if option_form.is_valid():
            option = option_form.save(commit=False)

            option.game = sopa
            option.save()

            return redirect(reverse('cursos:course_sopa', kwargs={'id': sopa.pk}))
        else:
            print(option_form.errors)
    

    context['option_form'] = option_form
    context['sopa'] = sopa
    context['course'] = course

    context = side_panel_context(context, user.pk, course.pk)

    return render(request, template_name, context)



def course_sopa_option_edit_view(request, id):
    context = {}
    template_name = template_prefix + 'sopa_option_form.html'
    user = request.user
    extended_user = user.extended_user

    option = get_object_or_404(SopaOption, pk=id)
    sopa = option.game
    course = sopa.modulo.curso

    option_form = SopaOptionForm(instance=option)


    if request.method == 'POST':
        option_form = SopaOptionForm(request.POST, instance=option)

        if option_form.is_valid():
            option = option_form.save()

            return redirect(reverse('cursos:course_sopa', kwargs={'id': sopa.pk}))
        else:
            print(option_form.errors)
    

    context['option_form'] = option_form
    context['sopa'] = sopa
    context['course'] = course

    context = side_panel_context(context, user.pk, course.pk)

    return render(request, template_name, context)


def course_sopa_option_delete_view(request, id):
    option = get_object_or_404(SopaOption, pk=id)
    sopa = option.game

    option.delete()
    return redirect(reverse('cursos:course_sopa', kwargs={'id': sopa.pk}))



def course_puzzle_view(request, id):
    context = {}
    template_name = template_prefix + 'puzzle.html'
    user = request.user
    extended_user = user.extended_user

    puzzle = get_object_or_404(PuzzleGame, pk=id)
    course = puzzle.modulo.curso
    options = puzzle.options.all()

    context['puzzle'] = puzzle
    context['course'] = course
    context['options'] = options

    context = side_panel_context(context, user.pk, course.pk)

    return render(request, template_name, context)


def course_puzzle_complete_view(request, id):
    context = {}
    template_name = template_prefix + 'puzzle_answer.html'

    puzzle = get_object_or_404(PuzzleGame, pk=id)
    
    if not puzzle.completions.filter(id=request.user.id).exists():
        puzzle.completions.add(request.user)

    context['puzzle'] = puzzle

    return render(request, template_name, context)


def course_puzzle_delete_view(request, id):
    context = {}
    template_name = template_prefix + 'puzzle_confirm_delete.html'
    user = request.user
    extended_user = user.extended_user

    puzzle = get_object_or_404(PuzzleGame, pk=id)
    course = puzzle.modulo.curso

    if request.method == 'POST':
        puzzle.delete()
        return redirect(reverse('cursos:course_detail', kwargs={'id': course.pk}))


    context['puzzle'] = puzzle
    context['course'] = course

    context = side_panel_context(context, user.pk, course.pk)

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
    modules = Modulo.objects.all().filter(curso=course.pk)

    viewed = False

    if user.is_authenticated:
        if user.watched_videos.filter(pk=id).exists():
            viewed = True

    context['viewed'] = viewed
    context['video'] = video
    context['course'] = course

    context = side_panel_context(context, user.pk, course.pk)

    return render(request, template_name, context)


@login_required
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

    viewed = False

    if user.is_authenticated:
        if user.read_lectures.filter(pk=id).exists():
            viewed = True

    context['viewed'] = viewed
    context['video'] = video
    context['course'] = course

    return render(request, template_name, context)


@login_required
def watch_video(request, id):
    video = get_object_or_404(Video, pk=id)
    
    if video.watches.filter(id=request.user.id).exists():
        video.watches.remove(request.user)
    else:
        video.watches.add(request.user)

    check_for_completion(request, video.modulo.curso.pk)

    return redirect(reverse('cursos:course_video', kwargs={'id': video.pk}))
