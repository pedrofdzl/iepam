from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

from users.models import ExtendedUser

User = get_user_model()

# Create your models here.
class Course(models.Model):
    owner = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name='own_courses')
    name = models.CharField("name", max_length=255)
    description = models.CharField("description", max_length=255)
    date_created = models.DateField()
    members = models.ManyToManyField(ExtendedUser, through='MemberOf')

    def __str__(self):
        return self.name


class MemberOf(models.Model):
    member = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name='courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_members')
    dateJoined = models.DateField()
    status = models.CharField('Status', default='Incompleto', max_length=255)

    def __str__(self):
        return f'{self.member.member.username} member of {self.course.name}'


    class Meta:
        verbose_name = 'MemberOf'
        verbose_name_plural = 'MembersOf'

        constraints = [
            models.constraints.UniqueConstraint(fields=['member', 'course'], name='membership')
        ]








class Quiz(models.Model):
    curso = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="quizzes", verbose_name="course") 
    name = models.CharField("name", max_length=255)
    description = models.CharField("description", max_length=255)

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
    # user = models.ForeignKey
    grade = models.FloatField("grade", validators=[MinValueValidator(0, "La calificacion no puede ser menor a 0"), MaxValueValidator(100, "La calificacion no puede ser mayor a 100")])
    