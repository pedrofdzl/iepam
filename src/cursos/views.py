from django.shortcuts import render
from django.http import JsonResponse,HttpResponse

# Create your views here.

def course(request):
    return render(request, 'cursos/course.html')