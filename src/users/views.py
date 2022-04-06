from turtle import update
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.http import Http404

from datetime import date

from .forms import RegisterForm, UserUpdateForm
from .models import ExtendedUser

User = get_user_model()

# Create your views here.

############################
######## Admin Views #######
############################

def user_register_view(request):
    context = {}

    register_form = RegisterForm()

    if request.method == "POST":
        register_form = RegisterForm(data=request.POST)

        if register_form.is_valid():
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
            
            user = User()
            extendedUser = ExtendedUser()

            user.first_name = first_name
            user.last_name = first_last_name
            user.password = password
            user.set_password(user.password)
            user.email = email

            user.save()

            extendedUser.user = user
            extendedUser.second_lastname = second_last_name
            extendedUser.birthdate = birthdate
            extendedUser.academic_level = academic_level

            if "cv" in request.FILES:
                extendedUser.cv = request.FILES["cv"]

            extendedUser.save()
                      
    context["form"] = register_form

    return render(request, "users/user_register.html", context)


def user_list_view(request):
    context = {}

    users = ExtendedUser.objects.all()
    
    context["users"] = users

    return render(request, "users/user_list.html", context)


def user_profile_view(request, id):

    user = get_object_or_404(User, pk=id)
    
    if request.user != user:
        raise Http404()

    return render(request, "")


def user_detail_view(request, id):
    context = {}

    user = get_object_or_404(User, pk=id)
    extended_user = user.extended_user

    context["extended_user"] = extended_user

    return render(request, "user/user_detail.html", context)


def user_update_view(request, id):
    
    user = get_object_or_404(User, pk=id)

    initial_data = {
        'first_name': user.first_name,
        'first_last_name': user.last_name,
        'second_last_name': user.extended_user.second_last_name,
        'day': user.extended_user.birthdate.day,
        'month': user.extended_user.birthdate.month,
        'year': user.extended_user.birthdate.year,
        'academic_level': user.extended_user.academic_level
    }

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
            user.extended


def user_delete_view(request, id):
    pass


def user_deactivate_view(request, id):
    context = {}

    user = get_object_or_404(User, pk=id)
    user.is_active = False
    user.save()

    return render(request, "", context)

