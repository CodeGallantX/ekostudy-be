from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def add(request):
    return HttpResponse('<h1>Add Course</h1>')