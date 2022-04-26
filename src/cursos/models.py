from email.policy import default
from pyexpat import model
from urllib.parse import MAX_CACHE_SIZE
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.contrib.auth import get_user_model

from users.models import ExtendedUser

from datetime import date
User = get_user_model()

# Create your models here.
class Course(models.Model):
    owner = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name='own_courses')
    name = models.CharField("name", max_length=255)
    description = models.CharField("description", max_length=255)
    date_created = models.DateField(default=date.today)
    members = models.ManyToManyField(ExtendedUser, through='MemberOf')
    likes = models.ManyToManyField(User, related_name="likes")

    def __str__(self):
        return self.name


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
    file = models.FileField('file', upload_to='entregas', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['.pdf', '.docx', '.xlsx', '.pptx'])])
    grade = models.FloatField('grade', validators=[MinValueValidator(-1), MaxValueValidator(100)])


class Video(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name="videos", verbose_name="modulo")
    name = models.CharField("name", max_length=255)
    description = models.CharField("description", max_length=255)
    url = models.URLField("url", max_length=255)

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
    weight = models.IntegerField("weight",validators=[MinValueValidator(0, "Ingresa un valor positivo"), MaxValueValidator(500, "El valor de la pregunta es demasiado grande")])


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options", verbose_name="question")
    prompt = models.CharField("prompt", max_length=255)
    correct = models.BooleanField("correct", default=False)


class QuizResult(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="results", verbose_name="quiz")
    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name='quiz_results', default=None)
    grade = models.FloatField("grade", validators=[MinValueValidator(0, "La calificacion no puede ser menor a 0"), MaxValueValidator(100, "La calificacion no puede ser mayor a 100")])
    