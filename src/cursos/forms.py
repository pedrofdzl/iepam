from django import forms

from .models import Course, Modulo, Lectura, Actividad, PuzzleGame, Question, Quiz, SopaGame, SopaOption, Video, QuestionOption, FileResource, HangmanGame, HangmanOption
from django.core.validators import MaxLengthValidator, FileExtensionValidator, MinLengthValidator


CV_MAX_SIZE = 1024 * 1024 * 5
# CV_MAX_SIZE = 5

def file_max_size(max_size: int):
    def helper(value):
        if value.size > max_size:
            raise forms.ValidationError('Archivo excede limite de espacio')
    return helper

PERMITTED_FILE_EXTENSIONS = [
    'pdf', 'docx', 'xlsx', 'pptx'
]

class CourseCreateForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description', 'bg_image']
        widgets = {
            'description': forms.Textarea()
        }
        validators = {
            'description': MaxLengthValidator(255),
            'bg_image': file_max_size(CV_MAX_SIZE)
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
    file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=PERMITTED_FILE_EXTENSIONS)])


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
    is_updating = False
    class Meta:
        model = QuestionOption
        fields = ['prompt', 'correct']

        widgets = {
            'prompt': forms.Textarea(attrs={'rows': 5})
        }

    def clean(self):
        all_cleaned_data = super().clean()
        question = self.instance.question
        correct = all_cleaned_data['correct']


        if len(QuestionOption.objects.filter(question=question)) >= 5 and not self.is_updating:
            raise forms.ValidationError('Solo puede haber un maximo de 5 preguntas')


        if correct:
            if QuestionOption.objects.filter(question=question).exists():
                options = question.options.all()
                if QuestionOption.objects.filter(pk=self.instance.pk).exists():
                    options = options.exclude(pk=self.instance.pk)


                for option in options:
                    if option.correct:
                        raise forms.ValidationError('¡Ya existe una respuesta correcta!')


class FileResourceForm(forms.ModelForm):
    class Meta:
        model = FileResource
        fields = ('title', 'description', 'resource')

        widgets = {
            'description': forms.Textarea(attrs={'rows': 3})
        }

class HangmanForm(forms.ModelForm):
    class Meta:
        model = HangmanGame
        fields = ('title', 'description')

        widgets = {
            'description': forms.Textarea(attrs={'rows':3})
        }

class HangmanOptionForm(forms.ModelForm):
    is_updating = False
    class Meta:
        model = HangmanOption
        fields = ('option', 'hint_1', 'hint_2')


    def clean(self):
        all_cleaned_data = super().clean()
        hangman = self.instance.game

        if len(HangmanOption.objects.filter(game=hangman)) >= 5 and not self.is_updating:
            raise forms.ValidationError('No pueden existir mas de 5 opciones')


    
    def clean_hint_1(self):
        hint_1 = self.cleaned_data['hint_1']

        hint_1 = hint_1.strip().split(' ')[0]
        return hint_1

    def clean_hint_2(self):
        hint_2 = self.cleaned_data['hint_2']

        hint_2 = hint_2.strip().split(' ')[0]
        return hint_2


class SopaForm(forms.ModelForm):
    class Meta:
        model = SopaGame
        fields = ('title', 'description')

        widgets = {
            'description': forms.Textarea(attrs={'rows':3})
        }

class SopaOptionForm(forms.ModelForm):
    is_updating = False
    class Meta:
        model = SopaOption
        fields = ('option',)


    def clean(self):
        all_cleaned_data = super().clean()
        game = self.instance.game

        if len(SopaOption.objects.filter(game=game)) >= 5 and not self.is_updating:
            raise forms.ValidationError('No se pueden tener mas de 5 opciones')

class PuzzleForm(forms.ModelForm):
    class Meta:
        model = PuzzleGame
        fields = ('title', 'description')

        widgets = {
            'description': forms.Textarea(attrs={'rows':3})
        }