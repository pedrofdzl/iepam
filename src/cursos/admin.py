from django.contrib import admin

from .models import Course, MemberOf
# Register your models here.
admin.site.register(Course)
admin.site.register(MemberOf)
