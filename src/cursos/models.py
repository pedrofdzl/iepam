from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.contrib.auth import get_user_model

from users.models import ExtendedUser

from datetime import date
from django.utils import timezone
User = get_user_model()
from pathlib import Path
from PIL import Image

import os



def resource_upload_handler(instance, filename):
    destination = Path('resources') / str(instance.modulo.name)

    extension = str(Path(filename).suffix)
    file = Path(instance.title + extension)

    destination = str(destination / file)
    return destination

def entrega_upload_handler(instance, filename):
    destination = Path('entregas') / str(instance.actividad.modulo.name) / str(instance.actividad.name)

    extension = str(Path(filename).suffix)
    file = Path(f'{instance.actividad.name}_{instance.user.user.username}' + extension)

    destination = str(destination / file)
    return destination

def course_image_upload_handler(instance, filename):
    destination = Path('cursos') / 'image' / str(instance.name)

    extension = str(Path(filename).suffix)
    file = Path(f'{instance.name}_image' + extension)

    destination = str(destination / file)
    return destination


PERMITTED_FILE_EXTENSIONS = [
    'pdf', 'docx', 'xlsx', 'pptx'
]

# Create your models here.
class Course(models.Model):
    owner = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name='own_courses')
    name = models.CharField("name", max_length=255)
    description = models.CharField("description", max_length=255)
    bg_image = models.ImageField('BG Image', upload_to=course_image_upload_handler, blank=True, null=True)
    date_created = models.DateField(default=date.today)
    members = models.ManyToManyField(ExtendedUser, through='MemberOf')
    likes = models.ManyToManyField(User, related_name="likes")

    def __str__(self):
        return self.name

    def delete(self):
        if self.bg_image and os.path.exists(self.bg_image.path):
            os.remove(self.bg_image.path)
        return super().delete()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # width = 1280
        # heigh = 960
        if self.bg_image:
            img = Image.open(self.bg_image.path)
            dimensions = (1280, 960)
            img.thumbnail(dimensions)
            img.save(self.bg_image.path)


# ? Approved Status:
# ? 'No Tomado', 'Cursando', 'Completado'
# ? Verify

class MemberOf(models.Model):
    member = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name='courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_members')
    dateJoined = models.DateField()
    status = models.CharField('Status', default='Cursando', max_length=255)

    def __str__(self):
        return f'{self.member.user.username} member of {self.course.name}'


    class Meta:
        verbose_name = 'MemberOf'
        verbose_name_plural = 'MembersOf'

        constraints = [
            models.constraints.UniqueConstraint(fields=['member', 'course'], name='membership')
        ]


class Modulo(models.Model):
    curso = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modulos', verbose_name='course')
    name = models.CharField('name', max_length=255)
    
    def __str__(self):
        return self.name

class Lectura(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='lecturas', verbose_name='modulo')
    name = models.CharField('name', max_length=255)
    description = models.CharField('description', max_length=255)
    content = models.CharField('content', max_length=2024, null=True, blank=True)
    author = models.CharField('author', max_length=255, null=True, blank=True)
    reads = models.ManyToManyField(User, related_name="read_lectures")

    def __str__(self):
        return self.name

class Actividad(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='actividades', verbose_name='modulo')
    name = models.CharField('name', max_length=255)
    description = models.CharField('description', max_length=255)
    instructions = models.CharField('instructions', max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Entrega(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='entregas', verbose_name='actividad')
    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name='entregas', verbose_name='users')
    created_date = models.DateTimeField(default=timezone.now) 
    file = models.FileField('file', upload_to=entrega_upload_handler, blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=PERMITTED_FILE_EXTENSIONS)])
    grade = models.FloatField('grade', validators=[MinValueValidator(-1), MaxValueValidator(100)], null=True, blank=True)


    def delete(self) ->tuple[int, dict[int, str]]:
        if os.path.exists(self.file.path):
            os.remove(self.file.path)
        
        return super().delete()


class Video(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name="videos", verbose_name="modulo")
    name = models.CharField("name", max_length=255)
    description = models.CharField("description", max_length=255)
    url = models.URLField("url", max_length=255)
    watches = models.ManyToManyField(User, related_name="watched_videos")

    def __str__(self):
        return self.name


class Quiz(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name="quizzes", verbose_name="modulo", default=None) 
    name = models.CharField("name", max_length=255)
    description = models.CharField("description", max_length=255)

    def __str__(self):
        return self.name


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions", verbose_name="quiz")
    prompt = models.CharField("prompt", max_length=255)
    # weight = models.IntegerField("weight",validators=[MinValueValidator(0, "Ingresa un valor positivo"), MaxValueValidator(500, "El valor de la pregunta es demasiado grande")])

    def __str__(self):
        return f'Question {self.prompt} for quiz'

class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options", verbose_name="question")
    prompt = models.CharField("prompt", max_length=255)
    correct = models.BooleanField("correct", default=False)


class QuizResult(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="results", verbose_name="quiz")
    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name='quiz_results', default=None)
    grade = models.FloatField("grade", validators=[MinValueValidator(0, "La calificacion no puede ser menor a 0"), MaxValueValidator(100, "La calificacion no puede ser mayor a 100")])
    

class FileResource(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='archivos')
    title = models.CharField('Titulo', max_length=255)
    description = models.CharField('Description', max_length=255)
    resource = models.FileField('Resource', upload_to=resource_upload_handler, validators=[FileExtensionValidator(allowed_extensions=PERMITTED_FILE_EXTENSIONS)])
    reads = models.ManyToManyField(User, related_name='viewed_resources')

    class Meta:
        verbose_name = 'File Resource'
        verbose_name_plural = 'File Resources'

    def __str__(self):
        return f'File: {self.title}'

    def delete(self) -> tuple[int, dict[str, int]]:
        if os.path.exists(self.resource.path):
            os.remove(self.resource.path)

        return super().delete()


class HangmanGame(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='hangmangames')
    title = models.CharField('Title', max_length=255)
    description = models.CharField('Description', max_length=255)
    completions = models.ManyToManyField(User, related_name="completed_hangmans")

    def __str__(self):
        return f'Hangman Game module: {self.modulo.name}-{self.title}'


class HangmanOption(models.Model):
    game = models.ForeignKey(HangmanGame, on_delete=models.CASCADE, related_name='options')
    option = models.CharField('Option', max_length=9)
    hint_1 = models.CharField('hint 1', max_length=255)
    hint_2 = models.CharField('hint_2', max_length=255)

    def __str__(self):
        return f'Hangman Game {self.game.title} option: {self.option}'


class SopaGame(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='sopagames')
    title = models.CharField('Title', max_length=255)
    description = models.CharField('Description', max_length=255)
    completions = models.ManyToManyField(User, related_name="completed_sopas")

    def __str__(self):
        return f'Sopa de Letras Game module: {self.modulo.name}-{self.title}'


class SopaOption(models.Model):
    game = models.ForeignKey(SopaGame, on_delete=models.CASCADE, related_name='options')
    option = models.CharField('Option', max_length=9)

    def __str__(self):
        return f'Sopa de Letras Game {self.game.title} option: {self.option}'


class PuzzleGame(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='puzzlegames')
    title = models.CharField('Title', max_length=255)
    description = models.CharField('Description', max_length=255)
    completions = models.ManyToManyField(User, related_name="completed_puzzles")

    def __str__(self):
        return f'Puzzle Game module: {self.modulo.name}-{self.title}'