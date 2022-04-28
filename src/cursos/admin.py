from django.contrib import admin

from .models import Course, MemberOf, Quiz, Question, QuestionOption
# Register your models here.
admin.site.register(Course)
admin.site.register(MemberOf)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(QuestionOption)