from django.contrib import admin

from .models import Course, MemberOf, Quiz, Question, QuestionOption, Modulo, FileResource, Actividad, Entrega, HangmanGame
# Register your models here.
admin.site.register(Course)
admin.site.register(MemberOf)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(QuestionOption)
admin.site.register(Modulo)
admin.site.register(FileResource)
admin.site.register(Actividad)
admin.site.register(Entrega)
admin.site.register(HangmanGame)