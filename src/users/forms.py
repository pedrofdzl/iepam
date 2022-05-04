from inspect import Attribute
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from datetime import date
from calendar import monthrange

from .models import ExtendedUser
import os

MONTHS = [
    (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
    (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
    (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
]


USER_TYPES = [
    ('', '----------'),
    ('Administradores', 'Administrador'),
    ('Capacitadores', 'Capacitador'),
    ('Estudiantes', 'Estudiante')
]

User = get_user_model()

CV_MAX_SIZE = 1024 * 1024 * 5
# CV_MAX_SIZE = 5

def file_max_size(max_size: int):
    def helper(value):
        if value.size > max_size:
            raise forms.ValidationError('Archivo excede limite de espacio')
    return helper

def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    extension = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf',]
    if not extension.lower() in valid_extensions:
        raise ValidationError('Solo se aceptan archivos pdf')


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=255, min_length=6)
    first_name = forms.CharField(max_length=255)
    first_last_name = forms.CharField(max_length=255)
    second_last_name = forms.CharField(max_length=255)
    email = forms.EmailField(max_length=255)
    user_type = forms.ChoiceField(choices=USER_TYPES)

    day = forms.IntegerField(max_value=31, min_value=1, initial=date.today().day, widget=forms.Select(choices=[(num, num) for num in range(1, 32)]))
    month = forms.IntegerField(max_value=12, min_value=1, initial=MONTHS[date.today().month-1], widget=forms.Select(choices=MONTHS))
    year = forms.IntegerField(min_value=1900, max_value=date.today().year, initial=date.today().year, widget=forms.Select(choices=[(year, year) for year in range(1900, date.today().year+1)]))

    academic_level = forms.CharField(max_length=255)
    password = forms.CharField(max_length=300, widget=forms.PasswordInput(attrs={'class':'password-input'}))
    v_password = forms.CharField(max_length=300, widget=forms.PasswordInput(attrs={'class':'password-input'}))
    cv = forms.FileField(required=False, validators=[
                                                        file_max_size(CV_MAX_SIZE), validate_file_extension],
                                                        widget=forms.FileInput(attrs={'class':'custom-file-input', 'id':'file'}))
    profile_pic = forms.ImageField(required=False, 
                                                        widget=forms.FileInput(attrs={'class':'custom-file-input', 'id':'file'}))
    


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        all_clean_data = super().clean()

        # Username uniqueness
        username = all_clean_data['username']

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Usuario ya esta registrado')

        # Password validation
        password = all_clean_data['password']
        v_password = all_clean_data['v_password']

        if password != v_password:
            raise forms.ValidationError('¡Los Passwords no coinciden!')


        # Validate Email is unique
        email = all_clean_data['email']

        email_exists = User.objects.filter(email=email).exists()
        if email_exists:
            raise forms.ValidationError('Este correo ya esta registrado.')


        # Birth Date Validation
        day = int(all_clean_data['day'])
        month = int(all_clean_data['month'])
        year = int(all_clean_data['year'])

        _, days = monthrange(year, month)

        if day > days:
            raise forms.ValidationError('No es una fecha Valida!')


        user_type = all_clean_data['user_type']
        if user_type == '':
            raise forms.ValidationError('Por favor escoger un un tipo de usuario')

        if not Group.objects.filter(name=user_type).exists():
            raise forms.ValidationError('Ese no es un grupo valido')



class UserUpdateForm(forms.Form):
    first_name = forms.CharField(max_length=255)
    first_last_name = forms.CharField(max_length=255)
    second_last_name = forms.CharField(max_length=255)

    day = forms.IntegerField(max_value=31, min_value=1, widget=forms.Select(
                                                                            choices=[(num, num) for num in range(1, 32)]
                                                                        ))
    month = forms.IntegerField(max_value=12, min_value=1, widget=forms.Select(choices=MONTHS))
    year = forms.IntegerField(min_value=1900, max_value=date.today().year, widget=forms.Select(
                                                                            choices=[(year, year) for year in range(1900, date.today().year+1)]
                                                                        ))

    academic_level = forms.CharField(max_length=255)
    profile_pic = forms.ImageField(required=False, 
                                                widget=forms.FileInput(attrs={'class':'custom-file-input', 'id':'file'}))


    def clean(self):
        all_clean_data = super().clean()

        day = int(all_clean_data['day'])
        month = int(all_clean_data['month'])
        year = int(all_clean_data['year'])

        _, days = monthrange(year, month)

        if days < day:
            raise forms.ValidationError('No es una fecha valida')


class UserCVForm(forms.ModelForm):
    cv = forms.FileField(validators=[file_max_size(CV_MAX_SIZE), validate_file_extension])
    class Meta:
        model = ExtendedUser
        fields = ('cv',)


class ProfilePicForm(forms.ModelForm):
    profile_pic = forms.ImageField(validators=[file_max_size(CV_MAX_SIZE)])
    class Meta:
        model = ExtendedUser
        fields = ('profile_pic',)


class UserChangeGroupForm(forms.Form):
    user_type = forms.ChoiceField(choices=USER_TYPES)

    def clean(self):
        all_cleaned_data = super().clean()

        user_type = all_cleaned_data['user_type']
        if user_type == '':
            raise forms.ValidationError('Por favor escoger un un tipo de usuario')

        if not Group.objects.filter(name=user_type).exists():
            raise forms.ValidationError('Ese no es un grupo valido')
