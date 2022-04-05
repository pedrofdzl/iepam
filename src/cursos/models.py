from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Course(models.Model):
    # owner = models.ForeignKey
    name = models.CharField("name", max_length=255)
    description = models.CharField("description", max_length=255)

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
    