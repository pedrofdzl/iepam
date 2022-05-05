import re
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from requests import get
from cursos.models import Course, Entrega, MemberOf, Modulo, Lectura, Actividad, Question, Video, Quiz, QuestionOption, QuizResult
from cursos.extras import act_completadas_curso, context_course_percentage, context_courses_percentage
from users.models import ExtendedUser
User = get_user_model()

def get_dashboard_context(request, context):
    user = request.user
    extended_user = user.extended_user

    cap_cursadas = 0
    cap_actuales = 0
    act_completadas = 0

    membersOf = MemberOf.objects.filter(member=user.pk)
    for memberOf in membersOf:
        if memberOf.status == 'Completado':
            cap_cursadas += 1
        if memberOf.status == 'Cursando':
            cap_actuales += 1

        act_completadas += act_completadas_curso(request, memberOf.course.pk)

    cap_creadas = extended_user.own_courses.count()

    context['cap_cursadas'] = cap_cursadas
    context['cap_actuales'] = cap_actuales
    context['cap_creadas'] = cap_creadas
    context['act_completadas'] = act_completadas
    context = context_courses_percentage(request, context)
    context = get_continue_context(request, context)

    return context


def get_continue_context(request, context):
    user = request.user
    extended_user = user.extended_user

    cursos = []
    progress = []

    membersOf = MemberOf.objects.filter(member=user.pk, status='Cursando').order_by('-dateJoined')

    if len(membersOf) > 3:
        for i in range(0, 3):
            cursos.append(membersOf[i].course)
            progress.append(context_course_percentage(membersOf[i].course))
    else:
        for mof in membersOf:
            cursos.append(mof.course)
            progress.append(context_course_percentage(request, mof.course.pk))

    context['continue_cursos'] = zip(cursos, progress)

    return context
