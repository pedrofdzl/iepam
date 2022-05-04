from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Course, Entrega, MemberOf, Modulo, Lectura, Actividad, Question, Video, Quiz, QuestionOption, QuizResult
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
