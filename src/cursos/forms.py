from email.policy import default
from django import forms

from django.core.validators import MaxLengthValidator

class CourseCreateForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea(), validators=[MaxLengthValidator(500)])

class ModuleAddForm(forms.Form):
    name = forms.CharField(max_length=255)

class LectureAddForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea(), validators=[MaxLengthValidator(2024)])

class ActivityAddForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea(), validators=[MaxLengthValidator(500)])

class VideoAddForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea(), validators=[MaxLengthValidator(500)])
    url = forms.URLField(max_length=255)