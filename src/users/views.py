from re import L
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, permission_required  

from django.http import Http404
from django.urls import reverse

from datetime import date

from .forms import RegisterForm, UserUpdateForm, UserCVForm
from .models import ExtendedUser

User = get_user_model()

template_prefix = 'users/'
# admin_template_pre = 'users/admin/'
admin_template_pre = 'users/'
# Create your views here.

############################
######## Admin Views #######
############################
@login_required
@permission_required(['users.is_admin'], raise_exception=True)
def aduser_member_register_View(request):
    context = {}
    template_name = admin_template_pre + 'user_register.html'

    register_form = RegisterForm()

    if request.method == "POST":
        register_form = RegisterForm(data=request.POST, files=request.FILES)

        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            first_name = register_form.cleaned_data["first_name"]
            first_last_name = register_form.cleaned_data["first_last_name"]
            second_last_name = register_form.cleaned_data["second_last_name"]
            email = register_form.cleaned_data["email"]
            
            day = int(register_form.cleaned_data["day"])
            month = int(register_form.cleaned_data["month"])
            year = int(register_form.cleaned_data["year"])

            birthdate = date(year, month, day)


            academic_level = register_form.cleaned_data["academic_level"]
            password = register_form.cleaned_data["password"]
            user_type = register_form.cleaned_data['user_type']

            user = User()
            extendedUser = ExtendedUser()
            group = get_object_or_404(Group, name=user_type)

                

            user.username = username
            user.first_name = first_name
            user.last_name = first_last_name
            user.password = password
            user.set_password(user.password)
            user.email = email

            user.save()

            user.groups.add(group)
            extendedUser.user = user
            extendedUser.second_last_name = second_last_name
            extendedUser.birthdate = birthdate
            extendedUser.academic_level = academic_level

            if user_type == 'Administradores':
                extendedUser.is_admin = True
                extendedUser.can_teach = True
            elif user_type == 'Capacitadores':
                extendedUser.can_teach = True


            if "cv" in request.FILES:
                extendedUser.cv = request.FILES["cv"]

            if "profile_pic" in request.FILES:
                extendedUser.profile_pic = request.FILES["profile_pic"]

            extendedUser.save()

            return redirect(reverse('users:user_detail', kwargs={'id':user.pk}))
                      
    context["form"] = register_form

    return render(request, template_name, context)


@login_required
@permission_required(['users.is_admin'])
def aduser_list_view(request):
    context = {}
    template_name = admin_template_pre + 'user_detail.html'

    users = ExtendedUser.objects.all()
    
    context["users"] = users

    return render(request, template_name, context)


@login_required
@permission_required(['users.is_admin'])
def aduser_detail_view(request, id):
    context = {}
    template_name = admin_template_pre + 'user_detail.html'

    user = get_object_or_404(User, pk=id)
    extended_user = user.extended_user

    incomplete_courses = extended_user.courses.filter(status='Cursando')

    context["extended_user"] = extended_user
    context['incomplete_courses'] = incomplete_courses

    return render(request, template_name, context)


@login_required
@permission_required(['users.is_admin'])
def aduser_update_view(request, id):
    context = {}
    template_name = admin_template_pre + 'user_profile_form_admin.html'

    user = get_object_or_404(User, pk=id)
    extended_user = user.extended_user

    initial_data = {
        'first_name': user.first_name,
        'first_last_name': user.last_name,
        'second_last_name': user.extended_user.second_last_name,
        'day': user.extended_user.birthdate.day,
        'month': user.extended_user.birthdate.month,
        'year': user.extended_user.birthdate.year,
        'academic_level': user.extended_user.academic_level
    }

    incomplete_courses = extended_user.courses.filter(status='Cursando')
    print(incomplete_courses)

    context['incomplete_courses'] = incomplete_courses
    context['extended_user'] = extended_user

    update_form = UserUpdateForm(initial=initial_data)

    if request.method == 'POST':
        update_form = UserUpdateForm(request.POST, initial=initial_data)

        if update_form.is_valid():

            first_name = update_form.cleaned_data['first_name']
            first_last_name = update_form.cleaned_data['first_last_name']
            second_last_name = update_form.cleaned_data['second_last_name']

            day = int(update_form.cleaned_data['day'])
            month = int(update_form.cleaned_data['month'])
            year = int(update_form.cleaned_data['year'])

            birthdate = date(year, month, day)

            academic_level = update_form.cleaned_data['academic_level']

            user.first_name = first_name
            user.last_name = first_last_name
            
            user.extended_user.second_last_name = second_last_name
            user.extended_user.academic_level = academic_level
            user.extended_user.birthdate = birthdate

            user.extended_user.save()
            user.save()

            return redirect(reverse('users:user_detail', kwargs={'id': user.pk}))

        else:
            print(update_form.errors)

    context["form"] = update_form
    context["extended_user"] = extended_user
    return render(request, template_name, context)


@login_required
@permission_required(['users.is_admin'])
def aduser_deactivate_view(request, id):
    context = {}
    template_name = admin_template_pre + "user_deactivate.html"
    user = get_object_or_404(User, pk=id)
    extended_user = user.extended_user


    if request.method == 'POST':
        user.is_active = False
        user.save()

        return redirect(reverse('users:user_detail', kwargs={'id': user.pk}))

    context['extended_user'] = extended_user

    return render(request, template_name, context)


@login_required
@permission_required(['users.is_admin'])
def aduser_activate_view(request, id):
    context = {}

    user = get_object_or_404(User, pk=id)
    
    user.is_active = True
    user.save()

    return redirect(reverse('users:user_detail', kwargs={'id':user.pk}))



# def aduser_change_cv(request, id):
#     context = {}
#     template_name = admin_template_pre + "user_cv_form.html"

#     initial_data = {
#         'cv': request.user.extended_user.cv
#     }

#     cv_form = UserCVForm(initial=initial_data)

#     if request.method == 'POST':
#         cv_form = UserCVForm(request.POST, initial=initial_data)

#         if cv_form.is_valid():
            
#             if 



############################
######## Member Views #######
############################
#@login_required(login_url='users:login')
@login_required
def memuser_profile_view(request):
    context = {}
    template_name = template_prefix + "user_profile.html"

    user = request.user
    extended_user = user.extended_user

    incomplete_courses = extended_user.courses.filter(status='Cursando')

    context["user"] = user
    context['incomplete_courses'] = incomplete_courses

    return render(request, template_name, context)


@login_required
def memuser_update_view(request):
    context = {}
    template_name = template_prefix + "user_profile_form.html"

    user = request.user

    initial_data = {
        'first_name': user.first_name,
        'first_last_name': user.last_name,
        'second_last_name': user.extended_user.second_last_name,
        'day': user.extended_user.birthdate.day,
        'month': user.extended_user.birthdate.month,
        'year': user.extended_user.birthdate.year,
        'academic_level': user.extended_user.academic_level
    }


    user_form = UserUpdateForm(initial=initial_data)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, initial=initial_data)

        if user_form.is_valid():
            
            first_name = user_form.cleaned_data['first_name']
            first_last_name = user_form.cleaned_data['first_last_name']
            second_last_name = user_form.cleaned_data['second_last_name']

            day = int(user_form.cleaned_data['day'])
            month = int(user_form.cleaned_data['month'])
            year = int(user_form.cleaned_data['year'])

            birthdate = date(year, month, day)

            academic_level = user_form.cleaned_data['academic_level']

            user.first_name = first_name
            user.last_name = first_last_name
            
            user.extended_user.second_last_name = second_last_name
            user.extended_user.academic_level = academic_level
            user.extended_user.birthdate = birthdate

            user.extended_user.save()
            user.save()

            return redirect(reverse('users:user_profile'))

        else:
            print(user_form.errors)

    context["form"] = user_form

    return render(request, template_name, context)


@login_required
def memuser_changeCV_view(request):
    template_name = template_prefix + 'user_changecv_form.html'
    context = {}

    user = request.user


    cv_form = UserCVForm(instance=user.extended_user)

    if request.method == 'POST':
        cv_form = UserCVForm(request.POST, instance=user.extended_user, files=request.FILES)

        if cv_form.is_valid():
            extended = cv_form.save(commit=False)

            if 'cv' in request.FILES:
                extended.cv = request.FILES['cv']
                extended.save()
        else:
            print(cv_form.errors)
    
    context['form'] = cv_form

    return render(request, template_name, context)




def user_login_view(request):
    context = {}
    template_name = template_prefix + 'user_login.html'
    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')


        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect(reverse('index'))
        else:
            error_message = 'Usuario o Contraseña Incorrecto!, Por favor vuelve a intentarlo'

    context['error_message'] = error_message

    return render(request, template_name, context)


def user_logout_view(request):
    logout(request)
    return redirect(reverse('index'))

