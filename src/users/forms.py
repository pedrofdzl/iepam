from mimetypes import init
from django import forms
from datetime import date
from calendar import monthrange

MONTHS = [
    (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
    (5, "Mayo"), (6, "Juni"), (7, "Julio"), (8, "Agosto"),
    (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
]


CV_MAX_SIZE = 1024 * 1024 * 5

def file_max_size(max_size: int):
    def helper(value):
        if value.size > max_size:
            raise forms.ValidationError('Archivo excede limite de espacio')
    return helper


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=255, min_length=6)
    first_name = forms.CharField(max_length=255)
    first_last_name = forms.CharField(max_length=255)
    second_last_name = forms.CharField(max_length=255)
    email = forms.EmailField(max_length=255)

    day = forms.IntegerField(max_value=31, min_value=1, initial=date.today().day)
    month = forms.IntegerField(max_value=12, min_value=1, initial=MONTHS[date.today().year-1])
    year = forms.IntegerField(min_value=1900, max_value=date.today().year, initial=date.today().year)

    academic_level = forms.CharField(max_length=255)
    password = forms.PasswordInput()
    v_password = forms.PasswordInput()
    cv = forms.FileField(required=False, validators=[file_max_size(CV_MAX_SIZE)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        all_clean_data = super().clean()

        # Password validation
        password = all_clean_data['password']
        v_password = all_clean_data['v_password']

        if password != v_password:
            raise forms.ValidationError('¡Los Passwords no coinciden!')


        # Birth Date Validation
        day = int(all_clean_data['day'])
        month = int(all_clean_data['month'])
        year = int(all_clean_data['year'])

        _, days = monthrange(year, month)

        if day > days:
            raise forms.ValidationError('No es una fecha Valida!')

    


    class Meta:
        widgets = {
            'day': forms.Select(choices=[(num, num) for num in range(1, 32)]),
            'month': forms.Select(choices=MONTHS),
            'year': forms.Select(choices=[(year, year) for year in range(1900, date.today().year+1)]),
        }


class UserUpdateForm(forms.Form):
    first_name = forms.CharField(max_length=255)
    first_last_name = forms.CharField(max_length=255)
    second_last_name = forms.CharField(max_length=255)

    day = forms.IntegerField(max_value=31, min_value=1)
    month = forms.IntegerField(max_value=12, min_value=1)
    year = forms.IntegerField(min_value=1900, max_value=date.today().year)

    academic_level = forms.CharField(max_length=255)


    class Meta:
        widgets = {
            'day': forms.Select(choices=[(num, num) for num in range(1, 32)]),
            'month': forms.Select(choices=MONTHS),
            'year': forms.Select(choices=[(year, year) for year in range(1900, date.today().year+1)])
        }

    def clean(self):
        all_clean_data = super().clean()

        day = int(all_clean_data['day'])
        month = int(all_clean_data['month'])
        year = int(all_clean_data['year'])

        _, days = monthrange(year, month)

        if days < day:
            raise forms.ValidationError('No es una fecha valida')