from django import forms

from .models import Course, Modulo, Lectura, Actividad, Question, Quiz, Video, QuestionOption
from django.core.validators import MaxLengthValidator, FileExtensionValidator, MinLengthValidator

class CourseCreateForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea()
        }
        validators = {
            'description': MaxLengthValidator(255)
        }

class ModuleAddForm(forms.ModelForm):
    class Meta:
        model = Modulo
        fields = ['name']

class LectureAddForm(forms.ModelForm):
    class Meta:
        model = Lectura
        fields = ['name', 'description', 'content', 'author']
        widgets = {
            'content': forms.Textarea()
        }
        validators = {
            'content': MaxLengthValidator(2024)
        }

class ActivityAddForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = ['name', 'description', 'instructions']
        widgets = {
            'description': forms.Textarea()
        }
        validators = {
            'description': MaxLengthValidator(500)
        }

class EntregaAddForm(forms.Form):
    file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['.pdf', '.docx', '.xlsx', '.pptx'])])

class VideoAddForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['name', 'description', 'url']
        widgets = {
            'description': forms.Textarea()
        }
        validators = {
            'description': MaxLengthValidator(500)
        }

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5})
        }
        validators = {
            'description': MaxLengthValidator(500)
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['prompt',]

        widgets = {
            'prompt': forms.Textarea(attrs={'rows': 5})
        }



class QuestionOptionsForm(forms.ModelForm):
    correct = forms.BooleanField(required=False)
    class Meta:
        model = QuestionOption
        fields = ['prompt', 'correct']

        widgets = {
            'prompt': forms.Textarea(attrs={'rows': 5})
        }