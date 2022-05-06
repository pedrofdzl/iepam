from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Course, Entrega, MemberOf, Modulo, Lectura, Actividad, Question, Video, Quiz, QuestionOption, QuizResult, FileResource, HangmanGame, SopaGame
from users.models import ExtendedUser
User = get_user_model()

def get_iframe_url(url: str) -> str:
    """
    Gets the url for embeded iframe base on the youtube link

    params url(str): A string containing the url

    returns str: a string with the url ready to use in an iframe tag
    """

    result = 'https://www.youtube.com/embed/'
      
    if 'youtu.be' in url:
        video_code = url[17:]
        return result + video_code
    elif 'youtube.com' in url:
        query_params = url.split('?')[1]
        query_params = query_params.split('v=')[1]
        code = query_params.split('&')[0]
        return result + code

def side_panel_context(context, userId, id):
    user = get_object_or_404(User, pk=userId)
    extended_user = user.extended_user

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

        total_items += module.actividades.all().count()
        for activity in module.actividades.all():
            if Entrega.objects.all().filter(actividad=activity.pk, user=user.pk).exists():
                completed_items += 1

        total_items += module.quizzes.all().count()
        for quiz in module.quizzes.all():
            if QuizResult.objects.all().filter(quiz=quiz.pk, user=user.pk).exists():
                completed_items += 1

        total_items += module.archivos.all().count()
        for archivo in module.archivos.all():
            if archivo in user.viewed_resources.all():
                completed_items += 1

        total_items += module.hangmangames.all().count()
        for hangman in module.hangmangames.all():
            if hangman in user.completed_hangmans.all():
                completed_items += 1

        total_items += module.sopagames.all().count()
        for sopa in module.sopagames.all():
            if sopa in user.completed_sopas.all():
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

    return context

def check_for_completion(request, id):
    user = request.user

    course = get_object_or_404(Course, pk=id)
    modules = Modulo.objects.filter(curso=id)

    # Calculo de actividades totales para el progreso
    total_items = 0
    completed_items = 0
    
    for module in modules:

        total_items += module.lecturas.all().count()
        for lecture in module.lecturas.all():
            if lecture.reads.filter(pk=user.pk).exists():
                completed_items += 1

        total_items += module.videos.all().count()
        for video in module.videos.all():
            if video.watches.filter(pk=user.pk).exists():
                completed_items += 1

        total_items += module.actividades.all().count()
        for activity in module.actividades.all():
            if Entrega.objects.all().filter(actividad=activity.pk, user=user.pk).exists():
                completed_items += 1

        total_items += module.quizzes.all().count()
        for quiz in module.quizzes.all():
            if QuizResult.objects.all().filter(quiz=quiz.pk, user=user.pk).exists():
                completed_items += 1

        total_items += module.archivos.all().count()
        for archivo in module.archivos.all():
            if archivo in user.viewed_resources.all():
                completed_items += 1

        total_items += module.hangmangames.all().count()
        for hangman in module.hangmangames.all():
            if hangman in user.completed_hangmans.all():
                completed_items += 1

        total_items += module.sopagames.all().count()
        for sopa in module.sopagames.all():
            if sopa in user.completed_sopas.all():
                completed_items += 1

    if total_items == completed_items and total_items > 0:
        memberOf = get_object_or_404(MemberOf, member=user.pk, course=course.pk)
        memberOf.status = "Completado"
        memberOf.save()
    else:
        memberOf = get_object_or_404(MemberOf, member=user.pk, course=course.pk)
        memberOf.status = "Cursando"
        memberOf.save()


def context_courses_percentage(request, context):
    user = request.user

    membersOf = MemberOf.objects.filter(member=user.pk, status='Cursando')

    courses_names = []
    courses_percentages = []
    courses_ratios = []

    for memberOf in membersOf:
        course = get_object_or_404(Course, pk=memberOf.course.pk)
        modules = Modulo.objects.filter(curso=course.pk)

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

            total_items += module.actividades.all().count()
            for activity in module.actividades.all():
                if Entrega.objects.all().filter(actividad=activity.pk, user=user.pk).exists():
                    completed_items += 1

            total_items += module.quizzes.all().count()
            for quiz in module.quizzes.all():
                if QuizResult.objects.all().filter(quiz=quiz.pk, user=user.pk).exists():
                    completed_items += 1

            total_items += module.archivos.all().count()
            for archivo in module.archivos.all():
                if archivo in user.viewed_resources.all():
                    completed_items += 1

            total_items += module.hangmangames.all().count()
            for hangman in module.hangmangames.all():
                if hangman in user.completed_hangmans.all():
                    completed_items += 1

            total_items += module.sopagames.all().count()
            for sopa in module.sopagames.all():
                if sopa in user.completed_sopas.all():
                    completed_items += 1

        if total_items > 0:
            completion_ratio = completed_items / total_items
            completion_percentage = int(completion_ratio * 100)
        
        courses_names.append(course.name)
        courses_percentages.append(int(completion_percentage))
        courses_ratios.append(completion_ratio)

    context['courses_percentages'] = zip(courses_names, courses_percentages, courses_ratios)

    return context


def act_completadas_curso(request, id):
    user = request.user

    modules = Modulo.objects.filter(curso=id)

    completed_items = 0
    
    for module in modules:

        for lecture in module.lecturas.all():
            if lecture.reads.filter(pk=user.pk).exists():
                completed_items += 1

        for video in module.videos.all():
            if video.watches.filter(pk=user.pk).exists():
                completed_items += 1

        for activity in module.actividades.all():
            if Entrega.objects.all().filter(actividad=activity.pk, user=user.pk).exists():
                completed_items += 1

        for quiz in module.quizzes.all():
            if QuizResult.objects.all().filter(quiz=quiz.pk, user=user.pk).exists():
                completed_items += 1

        for archivo in module.archivos.all():
            if archivo in user.viewed_resources.all():
                completed_items += 1

        for hangman in module.hangmangames.all():
            if hangman in user.completed_hangmans.all():
                completed_items += 1

        for sopa in module.sopagames.all():
            if sopa in user.completed_sopas.all():
                completed_items += 1

    return completed_items

def context_course_percentage(request, courseID):
    user = request.user

    modules = Modulo.objects.filter(curso=courseID)

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

        total_items += module.actividades.all().count()
        for activity in module.actividades.all():
            if Entrega.objects.all().filter(actividad=activity.pk, user=user.pk).exists():
                completed_items += 1

        total_items += module.quizzes.all().count()
        for quiz in module.quizzes.all():
            if QuizResult.objects.all().filter(quiz=quiz.pk, user=user.pk).exists():
                completed_items += 1

        total_items += module.archivos.all().count()
        for archivo in module.archivos.all():
            if archivo in user.viewed_resources.all():
                completed_items += 1

        total_items += module.hangmangames.all().count()
        for hangman in module.hangmangames.all():
            if hangman in user.completed_hangmans.all():
                completed_items += 1

        total_items += module.sopagames.all().count()
        for sopa in module.sopagames.all():
            if sopa in user.completed_sopas.all():
                completed_items += 1

    if total_items > 0:
        completion_ratio = completed_items / total_items
        completion_percentage = int(completion_ratio * 100)

    ans = [completion_ratio, completion_percentage]

    return ans